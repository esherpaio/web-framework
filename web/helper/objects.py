from operator import attrgetter
from typing import Callable


def none_aware_attrgetter(attr: str) -> Callable[[list], tuple[bool, any]]:
    """Attribute getter that accepts None values."""

    def wrap(item: list) -> tuple[bool, any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap


class Singleton(type):
    """Singleton metaclass."""

    _instances = {}

    def __call__(cls, *args, **kwargs) -> dict:
        if cls not in cls._instances:
            class_ = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = class_
        return cls._instances[cls]
