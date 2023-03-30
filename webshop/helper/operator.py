from operator import attrgetter
from typing import Callable


def none_aware_attrgetter(attr: str) -> Callable[[list], tuple[bool, any]]:
    def wrap(item: list) -> tuple[bool, any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap
