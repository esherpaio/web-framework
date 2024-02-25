import glob
import os
import threading
import time
from operator import attrgetter
from threading import Thread
from typing import Any, Callable

#
# Classes
#


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


#
# Functions
#


def remove_dir(path: str) -> None:
    """Remove the content of a directory."""
    if os.path.isdir(path):
        for file_ in glob.glob(f"{path.rstrip('/')}/*"):
            if os.access(file_, os.W_OK):
                os.remove(file_)


def remove_file(path: str, delay_s: int = 0) -> None:
    """Remove a file with an optional delay."""

    def remove() -> None:
        if delay_s:
            time.sleep(delay_s)
        if os.path.isfile(path):
            os.remove(path)

    Thread(target=remove, daemon=True).start()


def none_attrgetter(attr: str) -> Callable[[Any], tuple[bool, Any]]:
    """Attribute getter that accepts None values."""

    def wrap(item: list) -> tuple[bool, Any]:
        value = getter(item)
        return value is None, value

    getter = attrgetter(attr)
    return wrap
