from datetime import datetime
from typing import Callable, Type

import alembic.config
from flask import Blueprint, Flask

from web.auth import Auth, current_user
from web.cache import cache, cache_common, cache_manager
from web.config import config
from web.database.clean import clean_carts, clean_users
from web.database.client import conn
from web.libs import cdn
from web.libs.app import handle_frontend_error
from web.libs.logger import log
from web.locale import LocaleManager, current_locale
from web.mail import MailEvent, mail
from web.optimizer import optimizer
from web.redirector import Redirector
from web.syncer import Syncer
from web.syncer.object import (
    AppSettingSyncer,
    EmailStatusSyncer,
    FileTypeSyncer,
    OrderStatusSyncer,
    ProductLinkeTypeSyncer,
    ProductTypeSyncer,
    UserRoleSyncer,
)

#
# Classes
#


class FlaskWeb:
    def __init__(
        self,
        app: Flask | None = None,
        blueprints: list[Blueprint] | None = None,
        jinja_filters: dict[str, Callable] | None = None,
        jinja_globals: dict[str, Callable] | None = None,
        mail_events: dict[MailEvent | str, list[Callable]] | None = None,
        syncers: list[Type[Syncer]] | None = None,
        db_migrate: bool = False,
        db_hook: Callable | None = None,
        cache_hook: Callable | None = None,
    ) -> None:
        if blueprints is None:
            blueprints = []
        if jinja_filters is None:
            jinja_filters = {}
        if jinja_globals is None:
            jinja_globals = {}
        if mail_events is None:
            mail_events = {}
        if syncers is None:
            syncers = []

        if app is not None:
            self.init(
                app,
                blueprints,
                jinja_filters,
                jinja_globals,
                mail_events,
                syncers,
                db_migrate,
                db_hook,
                cache_hook,
            )

    def init(
        self,
        app: Flask,
        blueprints: list[Blueprint],
        jinja_filters: dict[str, Callable],
        jinja_globals: dict[str, Callable],
        mail_events: dict[MailEvent | str, list[Callable]],
        syncers: list[Type[Syncer]],
        db_migrate: bool,
        db_hook: Callable | None,
        cache_hook: Callable | None,
    ) -> None:
        self.setup_database(db_migrate, syncers, db_hook)
        self.setup_cache(cache_hook)
        self.setup_mail(mail_events)
        self.setup_flask(app, blueprints)
        self.setup_jinja(app, jinja_filters, jinja_globals)

    #
    # Setup
    #

    def setup_database(
        self,
        migrate: bool,
        syncers: list[Type[Syncer]],
        hook: Callable | None = None,
    ) -> None:
        # Migrate database
        if migrate:
            log.info("Migrating database")
            alembic.config.main(argv=["upgrade", "head"])

        # Run syncers
        default_syncers = [
            AppSettingSyncer,
            EmailStatusSyncer,
            FileTypeSyncer,
            OrderStatusSyncer,
            ProductLinkeTypeSyncer,
            ProductTypeSyncer,
            UserRoleSyncer,
        ]
        all_syncers = default_syncers + syncers
        log.info(f"Running {len(all_syncers)} syncers")
        for syncer in all_syncers:
            with conn.begin() as s:
                syncer.sync(s)

        # Run startup functions
        startup_funcs = [clean_carts, clean_users]
        log.info(f"Running {len(startup_funcs)} startup functions")
        for func in startup_funcs:
            try:
                func()
            except Exception:
                log.error(
                    f"Failed to run startup script {func.__name__}",
                    exc_info=True,
                )

        # Run database hook
        if hook is not None:
            log.info("Running database hook")
            hook()

    def setup_cache(self, hook: Callable | None = None) -> None:
        cache_manager.add_hook(cache_common)
        if hook is not None:
            cache_manager.add_hook(hook)
        cache_manager.add_hook(optimizer.del_cache)
        cache_manager.update(force=True)

    def setup_mail(self, events: dict[MailEvent | str, list[Callable]]) -> None:
        if config.EMAIL_METHOD:
            log.info(f"Configuring email method {config.EMAIL_METHOD}")
        else:
            log.warning("No email method configured")

        if events:
            log.info(f"Updating {len(events)} mail events")
            mail.events.update(events)

    def setup_flask(self, app: Flask, blueprints: list[Blueprint]) -> None:
        if config.APP_DEBUG:
            log.info("Enabling Flask debug mode")
            app.debug = True
        app.register_error_handler(Exception, handle_frontend_error)

        log.info(f"Registering {len(blueprints)} blueprints")
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

        Auth(app)
        if config.APP_OPTIMIZE:
            log.info("Enabling optimizer")
            optimizer.init(app)
        LocaleManager(app)
        Redirector(app)

    def setup_jinja(
        self,
        app: Flask,
        filters: dict[str, Callable],
        globals_: dict[str, Callable],
    ) -> None:
        app.context_processor(
            lambda: dict(
                now=datetime.utcnow(),
                cache=cache,
                config=config,
                current_user=current_user,
                current_locale=current_locale,
            )
        )

        filters.update(
            {
                "price": lambda a: f"{a:.{2}f}",
                "datetime": lambda a, b: a.strftime(b),
            }
        )
        for name, func in filters.items():
            app.add_template_filter(func, name=name)

        globals_.update({"cdn_url": cdn.url})
        for name, func in globals_.items():
            app.add_template_global(func, name=name)
