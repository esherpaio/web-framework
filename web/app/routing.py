from typing import Any

from flask import current_app, request
from werkzeug.local import LocalProxy

from web.cache import cache
from web.database.model import AppBlueprint, AppRoute


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


current_route: Any = LocalProxy(lambda: get_route())
current_blueprint: Any = LocalProxy(lambda: get_blueprint())
