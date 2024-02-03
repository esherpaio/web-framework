import threading
from operator import attrgetter
from typing import Any, Callable

#
# Classes
#


class Singleton(type):
    _instances: dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with _lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(
                        *args, **kwargs
                    )
        return cls._instances[cls]


#
# Functions
#


def none_aware_attrgetter(attr: str) -> Callable[[Any], tuple[bool, Any]]:
    """Attribute getter that accepts None values."""

    def wrap(item: list) -> tuple[bool, Any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap


#
# Variables
#

_lock = threading.Lock()
