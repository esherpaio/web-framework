from flask import Flask, request
from werkzeug import Response

from web.app.urls import redirect_with_query, url_for
from web.utils import Singleton

from .proxy import current_locale
from .utils import expects_locale, gen_locale, lacks_locale


class LocaleManager(metaclass=Singleton):
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init(app)

    def init(self, app: Flask) -> None:
        app.before_request(self.redirect_locale)
        app.url_defaults(self.set_locale_urls)
        app.add_template_global(self.get_locale_url, name="locale_url")
        app.after_request(self.set_locale)

    @staticmethod
    def redirect_locale() -> Response | None:
        if request.endpoint is None:
            return None
        if request.view_args is None:
            return None
        if lacks_locale(request.endpoint, request.view_args):
            request.view_args["_locale"] = current_locale.locale
            url = url_for(request.endpoint, **request.view_args)
            return redirect_with_query(url, code=301)
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
