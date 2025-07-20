import re
from typing import Any, Type

from sqlalchemy.orm import Session, make_transient

from web.database import conn
from web.database.model import Base
from web.logger import log


class Automator:
    @classmethod
    def log_start(cls) -> None:
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", cls.__name__).lower()
        log.info(f"Running task {name}")

    @classmethod
    def run(cls) -> None:
        raise NotImplementedError


class SeedSyncer(Automator):
    MODEL: Type[Base]
    KEY: str
    IGNORE_KEYS: list[str] = []
    SEEDS: list[Any]

    @classmethod
    def run(cls) -> None:
        assert issubclass(cls.MODEL, Base)
        assert isinstance(cls.KEY, str)
        assert isinstance(cls.SEEDS, list)

        cls.log_start()
        with conn.begin() as s:
            cls.sync_model(s)

    @classmethod
    def sync_model(cls, s: Session) -> None:
        for seed in cls.SEEDS:
            filters = {cls.KEY: getattr(seed, cls.KEY)}
            row = s.query(cls.MODEL).filter_by(**filters).first()
            if row:
                for key, value in seed.__dict__.items():
                    if key in cls.IGNORE_KEYS:
                        continue
                    if key.startswith("_") or key == cls.KEY:
                        continue
                    setattr(row, key, value)
            else:
                make_transient(seed)
                s.add(seed)
            s.flush()


class ApiSyncer(Automator):
    API_URL: str

    @classmethod
    def run(cls) -> None:
        raise NotImplementedError


class Processor(Automator):
    @classmethod
    def run(cls) -> None:
        raise NotImplementedError


class Cleaner(Automator):
    @classmethod
    def run(cls) -> None:
        raise NotImplementedError
