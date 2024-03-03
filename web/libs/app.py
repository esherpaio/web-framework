import fnmatch
import logging
from typing import Any

from flask import current_app, redirect, request, url_for
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from web.api.utils import ApiText, response
from web.config import config
from web.database.model import AppBlueprint, AppRoute
from web.i18n import _
from web.libs.cache import cache
from web.libs.errors import WebError
from web.libs.logger import log

#
# Routes
#


def is_endpoint(endpoint: str) -> bool:
    """Check if an endpoint exists."""
    try:
        current_app.url_map.iter_rules(endpoint)
    except KeyError:
        return False
    else:
        return True


def check_redirects() -> Response | None:
    """Check if a redirect exists for the current request."""
    for x in cache.redirects:
        if fnmatch.fnmatch(request.url, x.url_from):
            return redirect(x.url_to, code=301)


def get_route() -> AppRoute | None:
    """Get a route object for the current request."""
    for route in cache.routes:
        if route.endpoint == request.endpoint:
            return route


def get_blueprint() -> AppBlueprint | None:
    """Get a blueprint object for the current request."""
    for blueprint in cache.blueprints:
        if blueprint.name == request.blueprint:
            return blueprint


#
# Error handling
#


def handle_frontend_error(error: Exception) -> Response:
    """Handle frontend errors."""
    # Parse error information
    if isinstance(error, HTTPException):
        code = error.code
        if code is None:
            level = logging.ERROR
        elif 300 <= code <= 399 or code in [404, 405]:
            level = logging.WARNING
        else:
            level = logging.ERROR
    else:
        code = None
        level = logging.ERROR
    # Log error and redirect
    info = ["Frontend error", f"HTTP {code} {request.method} {request.full_path}"]
    exc_info = True if level >= logging.ERROR else False
    log.log(level, " - ".join(info), exc_info=exc_info)
    return redirect(url_for(config.ENDPOINT_ERROR))


def handle_backend_error(error: Exception) -> Response:
    """Handle backend errors."""
    # Parse error information
    if isinstance(error, WebError):
        code = error.code
        if error.translation_key is not None:
            message = _(error.translation_key)
        else:
            message = ApiText.HTTP_500
    else:
        code = 500
        message = ApiText.HTTP_500
    # Log error and return response
    info = [
        "Backend error",
        f"HTTP {code} {request.method} {request.full_path}",
        f"message {message}",
    ]
    if request.is_json:
        info.append(f"data {request.get_json()}")
    log.error(" - ".join(info), exc_info=True)
    return response(code, message)


#
# Variables
#

current_route: Any = LocalProxy(lambda: get_route())
current_blueprint: Any = LocalProxy(lambda: get_blueprint())
