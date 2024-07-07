from typing import Any, Callable, Type

from web.config import config
from web.database.client import conn

from .syncer import Syncer


def external_sync(f: Callable) -> Callable[..., None]:
    def wrap(*args, **kwargs) -> None:
        if not config.APP_SYNC_EXTERNAL:
            return
        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap


def sync_before(
    syncer: Type[Syncer],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        def wrap(*args, **kwargs) -> Any:
            with conn.begin() as s:
                syncer().sync(s)
            return f(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


def sync_after(
    syncer: Type[Syncer],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        def wrap(*args, **kwargs) -> Any:
            result = f(*args, **kwargs)
            with conn.begin() as s:
                syncer().sync(s)
            return result

        wrap.__name__ = f.__name__
        return wrap

    return decorate
