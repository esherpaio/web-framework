from typing import Callable, Type

from sqlalchemy.orm import validates

from web.database.errors import DbLengthError, DbEmailError, DbPhoneError
from web.database.model import Base
from web.helper.validation import is_email, is_phone, gen_slug


def check_str_len(
    length: int,
    *names: str,
) -> Callable[[Callable[..., any]], Callable[..., any]]:
    def decorate(f: Callable) -> Callable[..., any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: any) -> any:
            if isinstance(value, str):
                value = value.strip()
                if len(value) <= length:
                    raise DbLengthError
            return value

        return wrap

    return decorate


def check_email(*names: str) -> Callable[[Callable[..., any]], Callable[..., any]]:
    def decorate(f: Callable) -> Callable[..., any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: any) -> any:
            if isinstance(value, str):
                value = value.strip()
                if not is_email(value):
                    raise DbEmailError
            return value

        return wrap

    return decorate


def check_phone(*names: str) -> Callable[[Callable[..., any]], Callable[..., any]]:
    def decorate(f: Callable) -> Callable[..., any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: any) -> any:
            if isinstance(value, str):
                value = value.strip()
                if not is_phone(value):
                    raise DbPhoneError
            return value

        return wrap

    return decorate


def check_vat(*names: str) -> Callable[[Callable[..., any]], Callable[..., any]]:
    def decorate(f: Callable) -> Callable[..., any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: any) -> any:
            if isinstance(value, str):
                value = value.strip()
                if not is_phone(value):
                    raise DbPhoneError
            return value

        return wrap

    return decorate


def set_slug(*names: str) -> Callable[[Callable[..., any]], Callable[..., any]]:
    def decorate(f: Callable) -> Callable[..., any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: any) -> any:
            self.slug = gen_slug(value)
            return value

        return wrap

    return decorate
