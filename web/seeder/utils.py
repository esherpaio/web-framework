from typing import Callable

from web import config


def external_seed(f: Callable) -> Callable[..., None]:
    def wrap(*args, **kwargs) -> None:
        if not config.SEED_EXTERNAL:
            return
        return f(*args, **kwargs)

    wrap.__name__ = f.__name__
    return wrap
