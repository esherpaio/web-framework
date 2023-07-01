import urllib.parse
from typing import Callable, Type

from sqlalchemy.orm import validates

from web.database.model import Base
from web.helper.validation import gen_slug


def set_slug(*names: str) -> Callable[[Callable[..., any]], Callable[..., any]]:
    def decorate(f: Callable) -> Callable[..., any]:
        @validates(*names)
        def wrap(self: Type[Base], key: str, value: any) -> any:
            self.slug = gen_slug(value)
            return value

        return wrap

    return decorate
