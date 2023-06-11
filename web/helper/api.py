import json
from enum import StrEnum
from typing import Callable

from flask import Response, request

from web.i18n.base import _


class ApiText(StrEnum):
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
) -> tuple[any, bool] | None:
    # Get value and determine if key is contained
    value = request.json.get(key, default)
    has_key = key in request.json

    # Type checks
    if nullable and value is None:
        pass
    elif not isinstance(value, type_):
        raise TypeError
    elif not nullable and value is None:
        raise TypeError

    return value, has_key


def json_empty_str_to_none(f: Callable) -> Callable[..., Response]:
    def wrap(*args, **kwargs) -> Response:
        if request.is_json:
            for k, v in request.json.items():
                if isinstance(v, str) and not v:
                    request.json[k] = None
        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap


def create_links(mapping: dict[str, Callable], links: dict = None) -> dict:
    if links is None:
        links = {}

    for _name, func in mapping.items():
        if f".{_name}" in request.endpoint:
            func_links = {**func(**request.view_args)}
            links.update(func_links)

    return links
