from abc import ABCMeta, abstractmethod
from typing import Callable, Type

from flask import Response
from sqlalchemy.orm import Session

from webshop import config
from webshop.database.client import Conn


class Syncer(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def sync(s: Session) -> None:
        """Run a synchronizing function"""

        pass


class Seeder(metaclass=ABCMeta):
    @abstractmethod
    def seed(self, s: Session, count: int = 1) -> None:
        """Run a seeding function"""

        pass


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
            with Conn.begin() as s:
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
            with Conn.begin() as s:
                syncer().sync(s)
            return result

        wrap.__name__ = f.__name__
        return wrap

    return decorate
