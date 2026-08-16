from typing import Any

from .cache import cache
from .utils import cache_common


def __getattr__(name: str) -> Any:
    # Importing the in-memory cache should not start the background manager.
    # Applications that explicitly import cache_manager still get the singleton.
    if name == "cache_manager":
        from .manager import cache_manager

        return cache_manager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
