import fnmatch
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
    if isinstance(error, HTTPException):
        log.warning(f"Frontend error - HTTP {error.code} - message {error.description}")
    else:
        log.error("Frontend error", exc_info=True)
    return redirect(url_for(config.ENDPOINT_ERROR))


def handle_backend_error(error: Exception) -> Response:
    """Handle backend errors."""
    code: int
    message: str | ApiText
    if isinstance(error, WebError):
        code = getattr(error, "code", 500)
        translation_key = getattr(error, "translation_key", None)
        message = ApiText.HTTP_500
        if isinstance(translation_key, str):
            message = _(translation_key)
        log.warning(f"Backend error - code {code} - message {message}")
    else:
        data = None
        if request.is_json:
            data = request.get_json()
        log.error(f"Backend error - data {data}", exc_info=True)
        code, message = 500, ApiText.HTTP_500
    return response(code, message)


#
# Variables
#

current_route: Any = LocalProxy(lambda: get_route())
current_blueprint: Any = LocalProxy(lambda: get_blueprint())
