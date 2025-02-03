import json
from decimal import Decimal
from enum import StrEnum
from typing import Any

from flask import request
from sqlalchemy import String
from sqlalchemy.orm.attributes import InstrumentedAttribute
from werkzeug import Response

from web.database.errors import DbMaxLengthError, DbNullError, DbTypeError
from web.i18n import _

#
# Enumerators
#


class HttpText(StrEnum):
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
# Functions - responses
#


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def json_response(
    code: int = 200,
    message: str | StrEnum | None = None,
    data: list | dict | None = None,
    links: dict | None = None,
) -> Response:
    """Create a default API response."""
    if message is None:
        message = HttpText.HTTP_200
    if data is None:
        data = {}
    if links is None:
        links = {}
    value = json.dumps(
        {"code": code, "message": message, "data": data, "links": links},
        cls=JsonEncoder,
    )
    return Response(value, status=code, mimetype="application/json")


#
# Functions - casting
#


def get_cast_func(type_: Any) -> Any:
    if type_ is bool:
        return cast_bool
    elif type_ is Decimal:
        return cast_decimal
    else:
        return type_


def cast_bool(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() == "true"
    return value


def cast_decimal(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    elif isinstance(value, str):
        return Decimal(value)
    return value


#
# Functions - getters
#


def json_get(
    key: str,
    type_: Any,
    nullable: bool = True,
    default: Any = None,
    column: InstrumentedAttribute | None = None,
) -> tuple[Any, bool]:
    """Get a value from the request json."""
    if request.is_json and request.json is not None:
        cast = get_cast_func(type_)
        value = request.json.get(key, default)
        if value is not None:
            value = cast(value)
            type_ = type(value)
        has_key = key in request.json
    else:
        value = default
        has_key = False
    _validate(value, type_, nullable, column)
    return value, has_key


def args_get(
    key: str,
    type_: Any,
    nullable: bool = True,
    default: Any = None,
    column: InstrumentedAttribute | None = None,
) -> tuple[Any, bool]:
    """Get a value from the request args."""
    cast = get_cast_func(type_)
    value = request.args.get(key, default)
    if value is not None:
        value = cast(value)
        type_ = type(value)
    has_key = key in request.args
    _validate(value, type_, nullable, column)
    return value, has_key


#
# Functions - validators
#


def _validate(
    value: Any,
    type_: Any,
    nullable: bool,
    column: InstrumentedAttribute | None = None,
) -> None:
    if nullable and value is None:
        return
    # Parsing
    if type_ in (float, int):
        type_ = (float, int)
    # Validation
    if not isinstance(value, type_):
        raise DbTypeError
    elif not nullable and value is None:
        raise DbNullError
    elif (
        column is not None
        and isinstance(column.type, String)
        and column.type.length is not None
        and len(value) > column.type.length
    ):
        raise DbMaxLengthError(column.name)
