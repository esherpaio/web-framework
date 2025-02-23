from decimal import Decimal
from typing import Any, Optional, Type

import emoji
from sqlalchemy import Numeric, TypeDecorator

from web.utils.generators import gen_slug
from web.utils.validation import is_email, is_phone

from ..errors import (
    DbEmailError,
    DbMaxLengthError,
    DbMaxNumberError,
    DbMinLengthError,
    DbMinNumberError,
    DbPhoneError,
)

#
# Types
#


class AutoDecimal(TypeDecorator):
    impl = Numeric
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[Decimal]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            return Decimal(value)
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Optional[Decimal]:
        if value is None:
            return None
        return Decimal(value)

    @property
    def python_type(self) -> Type[Decimal]:
        return Decimal


default_price = AutoDecimal(10, 2, asdecimal=True)
default_vat = AutoDecimal(4, 3, asdecimal=True)
default_rate = AutoDecimal(12, 6, asdecimal=True)


#
# Validation
#


def val_phone(value: str | None) -> None:
    if isinstance(value, str):
        if not is_phone(value):
            raise DbPhoneError


def val_email(value: str | None) -> None:
    if isinstance(value, str):
        if not is_email(value):
            raise DbEmailError


def val_length(
    key: str,
    value: str | None,
    min_: int | None = None,
    max_: int | None = None,
) -> None:
    if isinstance(value, str):
        if min_ is not None and not min_ <= len(value):
            raise DbMinLengthError(key)
        if max_ is not None and not max_ >= len(value):
            raise DbMaxLengthError(key)


def val_number(
    key: str,
    value: int | float | None,
    min_: int | None = None,
    max_: int | None = None,
) -> None:
    if isinstance(value, (int, float)):
        if min_ is not None and not value >= min_:
            raise DbMinNumberError(key)
        if max_ is not None and not value <= max_:
            raise DbMaxNumberError(key)


#
# Conversion
#


def get_text(value: str | None) -> str | None:
    if value in ["-", " "]:
        return None
    if isinstance(value, str):
        return emoji.replace_emoji(value, replace="")
    return None


def get_slug(value: str | None) -> str | None:
    if isinstance(value, str):
        return gen_slug(value)
    return None


def get_lower(value: str | None) -> str | None:
    if isinstance(value, str):
        return value.lower()
    return None


def get_upper(value: str | None) -> str | None:
    if isinstance(value, str):
        return value.upper()
    return None
