import emoji
from sqlalchemy import Numeric

from web.database.errors import DbEmailError, DbLengthError, DbNumberError, DbPhoneError
from web.libs.parse import gen_slug, is_email, is_phone

#
# Types
#

default_price = Numeric(10, 4, asdecimal=False)
default_vat = Numeric(4, 2, asdecimal=False)
default_rate = Numeric(10, 4, asdecimal=False)


#
# Validation
#


def val_length(
    value: str | None,
    min_: int | None = None,
    max_: int | None = None,
) -> None:
    if isinstance(value, str):
        if min_ is not None:
            if not min_ <= len(value):
                raise DbLengthError
        if max_ is not None:
            if not max_ >= len(value):
                raise DbLengthError


def val_email(value: str | None) -> None:
    if isinstance(value, str):
        if not is_email(value):
            raise DbEmailError


def val_phone(value: str | None) -> None:
    if isinstance(value, str):
        if not is_phone(value):
            raise DbPhoneError


def val_number(
    value: int | float | None,
    min_: int | None = None,
    max_: int | None = None,
) -> None:
    if isinstance(value, (int, float)):
        if min_ is not None:
            if not value >= min_:
                raise DbNumberError
        if max_ is not None:
            if not value <= max_:
                raise DbNumberError


def get_slug(value: str | None) -> str | None:
    if isinstance(value, str):
        return gen_slug(value)


def get_lower(value: str | None) -> str | None:
    if isinstance(value, str):
        return value.lower()


def get_upper(value: str | None) -> str | None:
    if isinstance(value, str):
        return value.upper()


def parse_text(value: str | None) -> str | None:
    if value in ["-", " "]:
        return None
    if isinstance(value, str):
        return emoji.replace_emoji(value, replace="")
