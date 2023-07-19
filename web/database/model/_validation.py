import urllib.parse
from typing import Any, Callable, Type

from sqlalchemy.orm import validates

from web.database.errors import DbEmailError, DbLengthError, DbPhoneError, DbSlugError
from web.database.model import Base
from web.helper.validation import gen_slug, is_email, is_phone


def check_str_len(
    length: int,
    *names: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: Any) -> Any:
            if isinstance(value, str):
                value = value.strip()
                if len(value) <= length:
                    raise DbLengthError
            return value

        return wrap

    return decorate


def check_email(*names: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: Any) -> Any:
            if isinstance(value, str):
                value = value.lower().strip()
                if not is_email(value):
                    raise DbEmailError
            return value

        return wrap

    return decorate


def check_phone(*names: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: Any) -> Any:
            if isinstance(value, str):
                value = value.strip()
                if not is_phone(value):
                    raise DbPhoneError
            return value

        return wrap

    return decorate


def check_slug(*names: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: Any) -> Any:
            if isinstance(value, str):
                value = urllib.parse.urlsplit(value).path
                if not value:
                    raise DbSlugError
                if not value.startswith("/"):
                    value = f"/{value}"
                value = value.rstrip("/")
            return value

        return wrap

    return decorate


def set_slug(*names: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: Any) -> Any:
            self.slug = gen_slug(value)
            return value

        return wrap

    return decorate
