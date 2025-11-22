from datetime import datetime, timezone
from typing import Callable, Type

import alembic.config
from flask import Blueprint, Flask

from web import cdn
from web.app.error import handle_error
from web.app.redirector import Redirector
from web.app.urls import url_for
from web.auth import Auth, current_user
from web.automation import Automator, task
from web.cache import cache, cache_common, cache_manager
from web.i18n import translator
from web.locale import LocaleManager, current_locale
from web.logger import log
from web.mail import MailEvent, mail
from web.optimizer import optimizer
from web.setup import config
from web.setup.logging import patch_logging
from web.utils.generators import format_decimal


class Server:
    def setup_logging(self) -> None:
        patch_logging()

    def setup_i18n(self, dir_: str | None) -> None:
        if dir_ is None:
            return
        log.info(f"Loading translations from {dir_}")
        file_count = translator.load_dir(dir_)
        if file_count == 0:
            log.warning(f"No translation files found in {dir_}")

    def setup_database(
        self,
        migrate: bool,
        tasks: list[Type[Automator]],
        hook: Callable | None = None,
    ) -> None:
        # Migrate database
        if migrate:
            log.info("Migrating database")
            alembic.config.main(argv=["upgrade", "head"])

        # Run tasks
        default_tasks = [
            task.UserCleaner,
            task.CartCleaner,
            task.AppSettingSeedSyncer,
            task.EmailStatusSeedSyncer,
            task.FileTypeSeedSyncer,
            task.OrderStatusSeedSyncer,
            task.ProductLinkeTypeSeedSyncer,
            task.ProductTypeSeedSyncer,
            task.UserRoleSeedSyncer,
        ]
        all_tasks = default_tasks + tasks
        log.info(f"Running {len(all_tasks)} tasks")
        for task_ in all_tasks:
            task_.run()

        # Run database hook
        if hook is not None:
            log.info("Running database hook")
            try:
                hook()
            except Exception as e:
                log.error(f"Error running database hook: {e}")

    def setup_cache(self, hook: Callable | None = None) -> None:
        cache_manager.add_hook(cache_common)
        if hook is not None:
            cache_manager.add_hook(hook)
        cache_manager.add_hook(optimizer.del_cache)
        cache_manager.update(force=True)

    def setup_mail(self, events: dict[MailEvent | str, list[Callable]]) -> None:
        if config.MAIL_METHOD:
            log.info(f"Configuring email method {config.MAIL_METHOD}")
        else:
            log.warning("No email method configured")

        if events:
            log.info(f"Updating {len(events)} mail events")
            mail.events.update(events)

    def setup_flask(self, app: Flask, blueprints: list[Blueprint]) -> None:
        app.config["PREFERRED_URL_SCHEME"] = config.URL_SCHEME
        if config.DEBUG:
            log.info("Enabling Flask debug mode")
            app.debug = True
        app.register_error_handler(Exception, handle_error)

        log.info(f"Registering {len(blueprints)} blueprints")
        for blueprint in blueprints:
            app.register_blueprint(blueprint)

        Auth(app)
        if config.OPTIMIZER_ENABLED:
            log.info("Enabling optimizer")
            optimizer.init(app)
        LocaleManager(app)
        Redirector(app)

    def setup_jinja(
        self,
        app: Flask,
        filters: dict[str, Callable] | None = None,
        globals_: dict[str, Callable] | None = None,
    ) -> None:
        if filters is None:
            filters = {}
        if globals_ is None:
            globals_ = {}

        app.context_processor(
            lambda: dict(
                now=datetime.now(timezone.utc),
                datetime=datetime,
                timezone=timezone,
                cache=cache,
                config=config,
                current_user=current_user,
                current_locale=current_locale,
            )
        )

        filters["price"] = format_decimal
        filters["datetime"] = current_locale.format_datetime
        for name, func in filters.items():
            app.add_template_filter(func, name=name)

        globals_["cdn_url"] = cdn.url
        globals_["url_for"] = url_for
        for name, func in globals_.items():
            app.add_template_global(func, name=name)
