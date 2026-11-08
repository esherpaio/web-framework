from typing import Any

from flask import request
from werkzeug.local import LocalProxy

from web.cache import cache
from web.database.model import AppBlueprint, AppRoute


def get_route() -> AppRoute | None:
    for route in cache.routes:
        if route.endpoint == request.endpoint:
            return route
    return None


def get_blueprint() -> AppBlueprint | None:
    for blueprint in cache.blueprints:
        if blueprint.name == request.blueprint:
            return blueprint
    return None


current_route: Any = LocalProxy(lambda: get_route())
current_blueprint: Any = LocalProxy(lambda: get_blueprint())
