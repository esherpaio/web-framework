from decimal import Decimal
from typing import Any

from flask import request
from sqlalchemy import String
from sqlalchemy.orm.attributes import InstrumentedAttribute

from web.database.error import DbMaxLengthError, DbNullError, DbTypeError

#
# Casting
#


def get_cast_func(type_: Any) -> Any:
    if type_ is bool:
        return _cast_bool
    elif type_ is Decimal:
        return _cast_decimal
    else:
        return type_


def _cast_bool(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() == "true"
    return value


def _cast_decimal(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    elif isinstance(value, str):
        return Decimal(value)
    return value


#
# Getters
#


def json_get(
    key: str,
    type_: Any,
    nullable: bool = True,
    default: Any = None,
    column: InstrumentedAttribute | None = None,
) -> tuple[Any, bool]:
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
    cast = get_cast_func(type_)
    value = request.args.get(key, default)
    if value is not None:
        value = cast(value)
        type_ = type(value)
    has_key = key in request.args
    _validate(value, type_, nullable, column)
    return value, has_key


#
# Validators
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
