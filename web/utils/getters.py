from operator import attrgetter
from typing import Any, Callable


def none_attrgetter(attr: str) -> Callable[[Any], tuple[bool, Any]]:
    def wrap(item: list) -> tuple[bool, Any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap
