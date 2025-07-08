from typing import Any, Callable, Type

from web.setup import config

from .automator import Automator


def external_sync(f: Callable) -> Callable[..., None]:
    def wrap(*args, **kwargs) -> None:
        if not config.AUTOMATE_EXTERNAL:
            return
        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap


def sync_before(
    syncer: Type[Automator],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        def wrap(*args, **kwargs) -> Any:
            syncer().run()
            return f(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


def sync_after(
    syncer: Type[Automator],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        def wrap(*args, **kwargs) -> Any:
            result = f(*args, **kwargs)
            syncer().run()
            return result

        wrap.__name__ = f.__name__
        return wrap

    return decorate
