from typing import Callable, Type

from werkzeug import Response

from web.config import config
from web.database.client import conn
from web.syncer import Syncer


def external_sync(f: Callable) -> Callable[..., None]:
    def wrap(*args, **kwargs) -> None:
        if not config.APP_SYNC_EXT:
            return
        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap


def sync_before(
    syncer: Type[Syncer],
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    def decorate(f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            with conn.begin() as s:
                syncer().sync(s)
            return f(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


def sync_after(
    syncer: Type[Syncer],
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    def decorate(f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            result = f(*args, **kwargs)
            with conn.begin() as s:
                syncer().sync(s)
            return result

        wrap.__name__ = f.__name__
        return wrap

    return decorate
