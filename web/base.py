import time
from datetime import datetime
from threading import Thread
from typing import Callable

import alembic.config
from flask import Blueprint, Flask, redirect, request, url_for
from flask_login import LoginManager
from werkzeug import Response

from web import config
from web.database.clean import clean_carts, clean_users
from web.database.client import conn
from web.database.model import (
    Country,
    Currency,
    FlaskBlueprint,
    FlaskRoute,
    Language,
    OrderStatus,
    ProductLinkType,
    ProductType,
    Redirect,
    Region,
    Setting,
    User,
)
from web.database.model.file_type import FileType
from web.database.model.user_role import UserRole
from web.helper import cdn
from web.helper.cache import cache
from web.helper.errors import _handle_frontend_error
from web.helper.localization import (
    current_locale,
    expects_locale,
    gen_locale,
    lacks_locale,
)
from web.helper.logger import logger
from web.helper.redirects import check_redirects
from web.helper.user import cookie_loader, session_loader

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
        static_hook: Callable | None = None,
        sync_hook: Callable | None = None,
        cache_hook: Callable | None = None,
    ) -> None:
        if jinja_filter_hooks is None:
            jinja_filter_hooks = {}
        if jinja_global_hooks is None:
            jinja_global_hooks = {}

        self._app = app
        self._blueprints = blueprints
        self._jinja_filter_hooks = jinja_filter_hooks
        self._jinja_global_hooks = jinja_global_hooks
        self._accept_cookie_auth = accept_cookie_auth
        self._accept_request_auth = accept_request_auth
        self._static_hook = static_hook
        self._sync_hook = sync_hook
        self._cache_hook = cache_hook

        self._cached_at: datetime = datetime.utcnow()
        self._cache_active: bool = True

    #
    # Setup
    #

    def setup(self) -> "FlaskWeb":
        self.setup_flask()
        self.setup_jinja()
        self.setup_auth()
        self.setup_static()
        self.setup_database()
        self.setup_cache()
        self.setup_redirects()
        self.setup_locale()
        self.setup_error_handling()
        return self

    def setup_flask(self) -> None:
        # Setup Flask
        self._app.debug = config.APP_DEBUG
        self._app.secret_key = config.APP_SECRET
        for blueprint in self._blueprints:
            self._app.register_blueprint(blueprint)

    def setup_jinja(self) -> None:
        # Register context
        self._app.context_processor(_add_context)
        # Register filters
        self._app.add_template_filter(_get_price, name="price")
        self._app.add_template_filter(_get_datetime, name="datetime")
        for key, value in self._jinja_filter_hooks.items():
            self._app.add_template_filter(value, name=key)
        # Register globals
        self._app.add_template_global(_get_cdn_url, name="cdn_url")
        for key, value in self._jinja_global_hooks.items():
            self._app.add_template_global(value, name=key)

    def setup_auth(self) -> None:
        # Initialize Flask-Login
        manager = LoginManager(self._app)
        manager.session_protection = "basic"
        manager.login_view = config.ENDPOINT_LOGIN
        manager.anonymous_user = User
        # Register user loaders
        if self._accept_cookie_auth:
            manager.user_loader(cookie_loader)
        if self._accept_request_auth:
            manager.request_loader(session_loader)

    def setup_static(self) -> None:
        # Run static hook
        if self._static_hook is not None:
            self._static_hook(self._app)

    def setup_database(self) -> None:
        # Perform migrations
        alembic.config.main(argv=["upgrade", "head"])
        # Create settings
        with conn.begin() as s:
            if s.query(Setting).count() == 0:
                s.add(Setting())
        # Run hooks
        if self._sync_hook is not None:
            self._sync_hook(self._app)
        # Run startup scripts
        for func in [clean_carts, clean_users]:
            try:
                func()
            except Exception:
                logger.error(f"Failed to run startup script: {func.__name__}")

    def setup_redirects(self) -> None:
        # Register Flask hooks
        self._app.before_request(check_redirects)

    def setup_locale(self) -> None:
        # Register Flask hooks
        self._app.before_request(_check_locale)
        self._app.after_request(_set_locale)
        self._app.url_defaults(_set_urls)
        self._app.add_template_global(_get_locale_url, name="locale_url")

    def setup_error_handling(self) -> None:
        # Register Flask hooks
        self._app.register_error_handler(Exception, _handle_frontend_error)

    def setup_cache(self) -> None:
        self._cache_active = True
        self.update_cache(force=True)

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

    @property
    def _cache_expired(self) -> bool:
        if self._cached_at is None:
            return True
        with conn.begin() as s:
            setting = s.query(Setting).first()
        if not setting or setting.cached_at is None:
            return False
        return setting.cached_at > self._cached_at

    def _update_cache(self) -> None:
        logger.info("Updating cache")
        self._cached_at = datetime.utcnow()
        with conn.begin() as s:
            # fmt: off
            cache.countries = s.query(Country).order_by(Country.name).all()
            cache.currencies = s.query(Currency).order_by(Currency.code).all()
            cache.languages = s.query(Language).order_by(Language.code).all()
            cache.regions = s.query(Region).order_by(Region.name).all()
            cache.file_types = s.query(FileType).order_by(FileType.name).all()
            cache.order_statuses = s.query(OrderStatus).order_by(OrderStatus.order).all()
            cache.product_link_types = s.query(ProductLinkType).order_by(ProductLinkType.name).all()
            cache.product_types = s.query(ProductType).order_by(ProductType.name).all()
            cache.user_roles = s.query(UserRole).order_by(UserRole.name).all()
            cache.routes = s.query(FlaskRoute).all()
            cache.blueprints = s.query(FlaskBlueprint).all()
            cache.redirects = s.query(Redirect).order_by(Redirect.url_from.desc()).all()
            cache.setting = s.query(Setting).first()
            # fmt: on
        if self._cache_hook is not None:
            self._cache_hook(self._app)
        cache.delete_routes()

    def stop_cache(self) -> None:
        self._cache_active = False


#
# Functions - default
#


def _add_context() -> dict:
    return dict(cache=cache, config=config, current_locale=current_locale)


def _get_price(price: float, decimals: int = 2) -> str:
    return f"{price:.{decimals}f}"


def _get_datetime(datetime_: datetime, format_: str) -> str:
    return datetime_.strftime(format_)


def _get_cdn_url(path_: str) -> str:
    return cdn.url(path_)


#
# Functions - locale
#


def _check_locale() -> Response | None:
    if request.endpoint is None:
        return None
    if request.view_args is None:
        return None
    if lacks_locale(request.endpoint, request.view_args):
        request.view_args["_locale"] = current_locale.locale
        url = url_for(request.endpoint, **request.view_args)
        return redirect(url, code=301)


def _set_locale(resp: Response) -> Response:
    resp.set_cookie("locale", current_locale.locale)
    return resp


def _set_urls(endpoint: str, values: dict) -> None:
    if lacks_locale(endpoint, values):
        values["_locale"] = current_locale.locale


def _get_locale_url(language_code: str, country_code: str) -> str:
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
