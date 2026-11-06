from typing import Any, Callable, Type

from .automator import Automator


def sync_before(
    syncer: Type[Automator],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(f: Callable) -> Callable[..., Any]:
        def wrap(*args, **kwargs) -> Any:
            syncer().execute()
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
            syncer().execute()
            return result

        wrap.__name__ = f.__name__
        return wrap

    return decorate
