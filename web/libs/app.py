import logging
from typing import Any

from flask import current_app, redirect, request, url_for
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import Response
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from web.api.utils import ApiText, json_response
from web.cache import cache
from web.config import config
from web.database.model import AppBlueprint, AppRoute
from web.i18n import _
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
    return True


def has_argument(endpoint: str, arg: str) -> bool:
    """Check if an endpoint has a specific argument."""
    try:
        for rule in current_app.url_map.iter_rules(endpoint):
            if arg in rule.arguments:
                return True
    except KeyError:
        pass
    return False


def get_route() -> AppRoute | None:
    """Get a route object for the current request."""
    for route in cache.routes:
        if route.endpoint == request.endpoint:
            return route
    return None


def get_blueprint() -> AppBlueprint | None:
    """Get a blueprint object for the current request."""
    for blueprint in cache.blueprints:
        if blueprint.name == request.blueprint:
            return blueprint
    return None


#
# Error handling
#


def handle_frontend_error(error: Exception) -> Response:
    """Handle frontend errors."""
    # Parse error information
    if isinstance(error, HTTPException):
        code = error.code
    elif isinstance(error, NoResultFound):
        code = 404
    else:
        code = None
    # Determine log level
    if code is None or code >= 500:
        level = logging.ERROR
    else:
        level = logging.WARNING
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
            message = _(error.translation_key, **error.translation_kwargs)
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
    return json_response(code, message)


#
# Variables
#

current_route: Any = LocalProxy(lambda: get_route())
current_blueprint: Any = LocalProxy(lambda: get_blueprint())
