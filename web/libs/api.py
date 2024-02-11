import json
from enum import StrEnum
from typing import Any, Callable

from flask import request
from werkzeug import Response

from web.i18n.base import _
from web.libs.errors import APINullError, APITypeError

#
# Enumerators
#


class ApiText(StrEnum):
    """API response messages."""

    HTTP_200 = _("API_HTTP_200")
    HTTP_202 = _("API_HTTP_202")
    HTTP_204 = _("API_HTTP_204")
    HTTP_400 = _("API_HTTP_400")
    HTTP_401 = _("API_HTTP_401")
    HTTP_403 = _("API_HTTP_403")
    HTTP_404 = _("API_HTTP_404")
    HTTP_409 = _("API_HTTP_409")
    HTTP_410 = _("API_HTTP_410")
    HTTP_500 = _("API_HTTP_500")


#
# Functions
#


def response(
    code: int = 200,
    message: str | StrEnum | None = None,
    data: list | dict | None = None,
    links: dict | None = None,
) -> Response:
    """Create a default API response."""

    if message is None:
        message = ApiText.HTTP_200
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
    key: str, type_: Any, nullable: bool = True, default: Any = None
) -> tuple[Any, bool]:
    """Get a value from the request body."""

    if request.is_json and request.json is not None:
        value = request.json.get(key, default)
        data = request.json
    else:
        value = None
        data = {}

    has_key = key in data

    if type_ in (float, int):
        type_ = (float, int)

    if nullable and value is None:
        pass
    elif not isinstance(value, type_):
        raise APITypeError
    elif not nullable and value is None:
        raise APINullError

    return value, has_key


def args_get(
    key: str, type_: Any, nullable: bool = True, default: Any = None
) -> tuple[Any, bool]:
    """Get a value from the request args."""

    value = request.args.get(key, default, type_)
    has_key = key in request.args

    if nullable and value is None:
        pass
    elif not nullable and value is None:
        raise APINullError

    return value, has_key


#
# Decorators
#


def modify_request(
    mapping: dict[str, Callable],
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Modify the request body."""

    def decorate(f: Callable) -> Callable[..., None]:
        def wrap() -> None:
            if request.is_json and request.endpoint is not None:
                for name, func in mapping.items():
                    if f".{name}" in request.endpoint:
                        func(request.json)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


def modify_response(
    mapping: dict[str, Callable],
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Modify the response body."""

    def decorate(f: Callable) -> Callable[..., Response]:
        def wrap(resp: Response) -> Response:
            if (
                resp.is_json
                and request.endpoint is not None
                and request.view_args is not None
            ):
                for name, func in mapping.items():
                    if f".{name}" in request.endpoint:
                        return func(resp, **request.view_args)
            return resp

        wrap.__name__ = f.__name__
        return wrap

    return decorate
