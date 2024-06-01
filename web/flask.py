import time
from datetime import datetime
from threading import Thread
from typing import Callable, Type

import alembic.config
from flask import Blueprint, Flask, redirect, request, url_for
from flask_login import LoginManager
from werkzeug import Response

from web.config import config
from web.database.clean import clean_carts, clean_users
from web.database.client import conn
from web.database.model import (
    AppBlueprint,
    AppRoute,
    AppSetting,
    Country,
    Currency,
    FileType,
    Language,
    OrderStatus,
    ProductLinkType,
    ProductType,
    Redirect,
    Region,
    User,
    UserRole,
)
from web.libs import cdn
from web.libs.app import check_redirects, handle_frontend_error
from web.libs.auth import cookie_loader, session_loader
from web.libs.cache import cache
from web.libs.locale import current_locale, expects_locale, gen_locale, lacks_locale
from web.libs.logger import log
from web.mail import MailEvent, mail
from web.optimizer import optimizer
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
        app: Flask,
        blueprints: list[Blueprint],
        jinja_filter_hooks: dict[str, Callable] | None = None,
        jinja_global_hooks: dict[str, Callable] | None = None,
        accept_cookie_auth: bool = False,
        accept_request_auth: bool = False,
        mail_events: dict[MailEvent | str, list[Callable]] | None = None,
        syncers: list[Type[Syncer]] | None = None,
        db_hook: Callable | None = None,
        cache_hook: Callable | None = None,
    ) -> None:
        if jinja_filter_hooks is None:
            jinja_filter_hooks = {}
        if jinja_global_hooks is None:
            jinja_global_hooks = {}
        if mail_events is None:
            mail_events = {}
        if syncers is None:
            syncers = []

        self._app = app
        self._blueprints = blueprints
        self._jinja_filter_hooks = jinja_filter_hooks
        self._jinja_global_hooks = jinja_global_hooks
        self._accept_cookie_auth = accept_cookie_auth
        self._accept_request_auth = accept_request_auth
        self._mail_events = mail_events
        self._syncers = syncers
        self._db_hook = db_hook
        self._cache_hook = cache_hook

        self._cached_at: datetime = datetime.utcnow()
        self._cache_active: bool = True

    #
    # Setup
    #

    def setup(self) -> "FlaskWeb":
        self.setup_flask()
        self.setup_jinja()
        self.setup_database()
        self.setup_optimizer()
        self.setup_auth()
        self.setup_mail()
        self.setup_cache()
        self.setup_redirects()
        self.setup_locale()
        self.setup_error_handling()
        return self

    def setup_flask(self) -> None:
        # Setup Flask
        if config.APP_DEBUG:
            log.info("Enabling debug mode")
        self._app.debug = config.APP_DEBUG
        self._app.secret_key = config.APP_SECRET

        # Register blueprints
        log.info(f"Registering {len(self._blueprints)} blueprints")
        for blueprint in self._blueprints:
            self._app.register_blueprint(blueprint)

    def setup_jinja(self) -> None:
        # Register context
        self._app.context_processor(
            lambda: dict(cache=cache, config=config, current_locale=current_locale)
        )

        # Register filters
        self._jinja_filter_hooks.update(
            {
                "price": lambda a: f"{a:.{2}f}",
                "datetime": lambda a, b: a.strftime(b),
            }
        )
        for name, func in self._jinja_filter_hooks.items():
            self._app.add_template_filter(func, name=name)

        # Register globals
        self._jinja_global_hooks.update(
            {
                "cdn_url": cdn.url,
            }
        )
        for name, func in self._jinja_global_hooks.items():
            self._app.add_template_global(func, name=name)

    def setup_auth(self) -> None:
        # Initialize Flask-Login
        manager = LoginManager(self._app)
        manager.session_protection = "basic"
        manager.login_view = config.ENDPOINT_LOGIN
        manager.anonymous_user = User

        # Register cookie loader
        if self._accept_cookie_auth:
            log.info("Accepting cookie authentication")
            manager.user_loader(cookie_loader)

        # Register request loader
        if self._accept_request_auth:
            log.info("Accepting bearer authentication")
            manager.request_loader(session_loader)

    def setup_database(self) -> None:
        # Migrate database
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
        all_syncers = default_syncers + self._syncers
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
        if self._db_hook is not None:
            log.info("Running database hook")
            self._db_hook()

    def setup_optimizer(self) -> None:
        if config.APP_OPTIMIZE:
            log.info("Enabling optimizer")
            optimizer.init(self._app)

    def setup_redirects(self) -> None:
        # Register Flask hooks
        if cache.redirects:
            log.info(f"Registering {len(cache.redirects)} redirects")
            self._app.before_request(check_redirects)

    def setup_locale(self) -> None:
        # Register Flask hooks
        self._app.before_request(self.redirect_locale)
        self._app.url_defaults(self.set_locale_urls)
        self._app.add_template_global(self.get_locale_url, name="locale_url")
        self._app.after_request(self.set_locale)

    def setup_error_handling(self) -> None:
        # Register Flask hooks
        self._app.register_error_handler(Exception, handle_frontend_error)

    def setup_mail(self) -> None:
        # Log status
        if config.EMAIL_METHOD:
            log.info(f"Configuring email method {config.EMAIL_METHOD}")
        else:
            log.warning("No email method configured")

        # Update mail events
        if self._mail_events:
            log.info(f"Updating {len(self._mail_events)} mail events")
            mail.EVENTS.update(self._mail_events)

    def setup_cache(self) -> None:
        # Start cache reloading
        self._cache_active = True
        self.update_cache(force=True)

    #
    # Locale
    #

    @staticmethod
    def redirect_locale() -> Response | None:
        if request.endpoint is None:
            return None
        if request.view_args is None:
            return None
        if lacks_locale(request.endpoint, request.view_args):
            request.view_args["_locale"] = current_locale.locale
            url = url_for(request.endpoint, **request.view_args)
            return redirect(url, code=301)
        return None

    @staticmethod
    def set_locale_urls(endpoint: str, values: dict) -> None:
        if lacks_locale(endpoint, values):
            values["_locale"] = current_locale.locale

    @staticmethod
    def get_locale_url(language_code: str, country_code: str) -> str:
        if request.endpoint is None:
            return ""
        if request.view_args is not None:
            kwargs = request.view_args.copy()
        else:
            kwargs = {}
        if expects_locale(request.endpoint):
            locale = gen_locale(language_code, country_code)
            kwargs["_locale"] = locale
        return url_for(request.endpoint, **kwargs, _external=True)

    @staticmethod
    def set_locale(resp: Response) -> Response:
        resp.set_cookie("locale", current_locale.locale)
        return resp

    #
    # Cache
    #

    def update_cache(self, force: bool = False) -> None:
        if not force:
            try:
                time.sleep(60)
            except Exception:
                return
        if self._cache_active:
            Thread(target=self.update_cache, daemon=True).start()
        if force or self._cache_expired:
            self._update_cache()

    def _update_cache(self) -> None:
        log.info("Updating cache")
        self._cached_at = datetime.utcnow()
        with conn.begin() as s:
            # fmt: off
            cache.blueprints = s.query(AppBlueprint).all()
            cache.countries = s.query(Country).order_by(Country.name).all()
            cache.currencies = s.query(Currency).order_by(Currency.code).all()
            cache.file_types = s.query(FileType).order_by(FileType.name).all()
            cache.languages = s.query(Language).order_by(Language.code).all()
            cache.order_statuses = s.query(OrderStatus).order_by(OrderStatus.order).all()
            cache.product_link_types = s.query(ProductLinkType).order_by(ProductLinkType.name).all()
            cache.product_types = s.query(ProductType).order_by(ProductType.name).all()
            cache.redirects = s.query(Redirect).order_by(Redirect.url_from.desc()).all()
            cache.regions = s.query(Region).order_by(Region.name).all()
            cache.routes = s.query(AppRoute).all()
            cache.setting = s.query(AppSetting).first()
            cache.user_roles = s.query(UserRole).order_by(UserRole.name).all()
            # fmt: on
        if self._cache_hook is not None:
            self._cache_hook(self._app)
        optimizer.del_cache()

    @property
    def _cache_expired(self) -> bool:
        if self._cached_at is None:
            return True
        with conn.begin() as s:
            setting = s.query(AppSetting).first()
        if not setting or setting.cached_at is None:
            return False
        return setting.cached_at > self._cached_at
