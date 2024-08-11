from typing import Any, Type

from sqlalchemy.orm import Session

from web.database.model import Base

from .automator import Automator


class Syncer(Automator):
    MODEL: Type[Base]
    KEY: str
    SEEDS: list[Any]

    @classmethod
    def run(cls, s: Session) -> None:
        cls.sync_model(s)

    @classmethod
    def sync_model(cls, s: Session) -> None:
        for seed in cls.SEEDS:
            filters = {cls.KEY: getattr(seed, cls.KEY)}
            row = s.query(cls.MODEL).filter_by(**filters).first()
            if row:
                for key, value in seed.__dict__.items():
                    if key.startswith("_") or key == cls.KEY:
                        continue
                    setattr(row, key, value)
            else:
                s.add(seed)
            s.flush()
