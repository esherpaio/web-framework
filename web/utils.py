import os
import threading
import time
from operator import attrgetter
from threading import Thread
from typing import Any, Callable

_lock = threading.Lock()


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


def remove_file(path: str, delay_s: int = 0) -> None:
    def remove() -> None:
        if delay_s:
            time.sleep(delay_s)
        if os.path.isfile(path):
            os.remove(path)

    Thread(target=remove, daemon=True).start()


def none_attrgetter(attr: str) -> Callable[[Any], tuple[bool, Any]]:
    def wrap(item: list) -> tuple[bool, Any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap
