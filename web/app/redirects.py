import fnmatch

from flask import Flask, redirect, request
from werkzeug import Response

from web.cache import cache


class Redirector:
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init(app)

    def init(self, app: Flask) -> None:
        app.before_request(self.check_redirects)

    @staticmethod
    def check_redirects() -> Response | None:
        for x in cache.redirects:
            if fnmatch.fnmatch(request.url, x.url_from):
                return redirect(x.url_to, code=301)
        return None
