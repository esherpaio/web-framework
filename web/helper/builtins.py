from operator import attrgetter
from typing import Any, Callable

#
# Functions
#


def none_aware_attrgetter(attr: str) -> Callable[[list], tuple[bool, Any]]:
    """Attribute getter that accepts None values."""

    def wrap(item: list) -> tuple[bool, Any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap
