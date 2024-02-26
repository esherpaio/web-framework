from abc import ABCMeta, abstractmethod
from typing import Any, Type

from sqlalchemy.orm import Session

from web.database.model import Base


class Syncer:
    MODEL: Type[Base]
    KEY: str
    SEEDS: list[Any]

    @classmethod
    def sync(cls, s: Session) -> None:
        for seed in cls.SEEDS:
            filters = {cls.KEY: getattr(seed, cls.KEY)}
            row = s.query(cls.MODEL).filter_by(**filters).first()
            if not row:
                s.add(seed)
                s.flush()


class Seeder(metaclass=ABCMeta):
    @abstractmethod
    def seed(self, s: Session, count: int = 1) -> None:
        pass
