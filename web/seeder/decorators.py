from typing import Callable, Type

from flask import Response

from web import config
from web.database.client import conn
from web.seeder.abc import Syncer


def external_seed(f: Callable) -> Callable[..., None]:
    def wrap(*args, **kwargs) -> None:
        if not config.SEED_EXTERNAL:
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
