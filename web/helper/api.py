import json
from enum import StrEnum
from typing import Callable

from flask import Response, redirect, request, url_for
from flask_login import current_user

from web import config
from web.database.model import UserRoleLevel
from web.i18n.base import _


class ApiText(StrEnum):
    """API response messages."""

    HTTP_200 = _("API_HTTP_200")
    HTTP_202 = _("API_HTTP_202")
    HTTP_400 = _("API_HTTP_400")
    HTTP_401 = _("API_HTTP_401")
    HTTP_403 = _("API_HTTP_403")
    HTTP_404 = _("API_HTTP_404")
    HTTP_409 = _("API_HTTP_409")
    HTTP_410 = _("API_HTTP_410")
    HTTP_500 = _("API_HTTP_500")


def response(
    code: int = 200,
    message: str | StrEnum = ApiText.HTTP_200,
    data: list | dict | None = None,
    links: dict | None = None,
) -> Response:
    """Create a default API response."""

    if data is None:
        data = {}
    if links is None:
        links = {}
    body = json.dumps(
        {
            "code": code,
            "message": message,
            "data": data,
            "links": links,
        }
    )
    return Response(
        body,
        status=code,
        mimetype="application/json",
    )


def json_get(
    key: str,
    type_: any,
    nullable: bool = True,
    default: any = None,
    allow_empty_str: bool = True,
) -> tuple[any, bool] | None:
    """Get a value from the request body."""

    value = request.json.get(key, default)
    has_key = key in request.json
    if value == "" and not allow_empty_str:
        value = None
    if nullable and value is None:
        pass
    elif not isinstance(value, type_):
        raise TypeError
    elif not nullable and value is None:
        raise TypeError
    return value, has_key


def create_links(mapping: dict[str, Callable], links: dict = None) -> dict:
    """Inject links into the response body."""

    if links is None:
        links = {}
    for _name, func in mapping.items():
        if f".{_name}" in request.endpoint:
            func_links = {**func(**request.view_args)}
            links.update(func_links)
    return links


def authorize(
    level: UserRoleLevel,
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Authorize a user based on their role level."""

    def decorate(f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            if current_user.is_authenticated and current_user.role.level >= level:
                return f(*args, **kwargs)
            elif "api" in request.blueprint:
                return response(403, ApiText.HTTP_403)
            else:
                return redirect(url_for(config.ENDPOINT_LOGIN))

        wrap.__name__ = f.__name__
        return wrap

    return decorate
