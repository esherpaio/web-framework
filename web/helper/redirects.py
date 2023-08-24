import fnmatch

from flask import redirect, request
from werkzeug import Response

from web.helper.cache import cache

#
# Functions
#


def check_redirects() -> Response | None:
    for x in cache.redirects:
        if fnmatch.fnmatch(request.url, x.url_from):
            return redirect(x.url_to, code=301)
