import fnmatch

from flask import Flask, request
from werkzeug import Response

from web.cache import cache

from .urls import redirect_with_query


class Redirector:
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init(app)

    def init(self, app: Flask) -> None:
        app.before_request(self.redirect)

    @staticmethod
    def redirect() -> Response | None:
        for x in cache.redirects:
            if fnmatch.fnmatch(request.url, x.url_from):
                return redirect_with_query(x.url_to, code=301)
        return None
