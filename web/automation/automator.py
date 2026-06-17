import re
from datetime import UTC, datetime, timedelta
from typing import Any, Type

import requests
from sqlalchemy.orm import Session

from web.database import conn
from web.database.model import AppSettings, Base
from web.logger import log
from web.setup import config


class Automator:
    RUN_DEBUG: bool = True
    INTERVAL_S: int | None = None

    @classmethod
    def log_start(cls) -> None:
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", cls.__name__).lower()
        log.info(f"Running task {name}")

    @classmethod
    def should_run(cls) -> bool:
        if cls.INTERVAL_S is None:
            return True
        with conn.begin() as s:
            settings = s.query(AppSettings).first()
            last_run = settings.automator.get(cls.__name__)
        if last_run is None:
            return True
        elapsed = datetime.now(UTC) - datetime.fromisoformat(last_run)
        return elapsed >= timedelta(seconds=cls.INTERVAL_S)

    @classmethod
    def mark_run(cls) -> None:
        with conn.begin() as s:
            settings = s.query(AppSettings).first()
            settings.automator[cls.__name__] = datetime.now(UTC).isoformat()

    @classmethod
    def run(cls) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__


class SeedSyncer(Automator):
    MODEL: Type[Base]
    KEY: str
    IGNORE_KEYS: list[str] = []
    SEEDS: list[Any]

    @classmethod
    def run(cls) -> None:
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
                s.merge(seed)
            s.flush()


class ApiSyncer(Automator):
    API_URL: str
    RUN_DEBUG: bool = False

    @classmethod
    def run(cls) -> None:
        raise NotImplementedError


class RestCountriesApiSyncer(ApiSyncer):
    INTERVAL_S = 604800

    @classmethod
    def fetch_all(cls, url) -> list[Any]:
        objects: list[Any] = []
        offset = 0
        while True:
            response = requests.request(
                "GET",
                url,
                timeout=config.AUTOMATE_TIMEOUT_S,
                headers={"Authorization": f"Bearer {config.REST_COUNTRIES_API_KEY}"},
                params={"offset": offset},
            )
            response.raise_for_status()
            data = response.json()["data"]
            objects.extend(data["objects"])
            meta = data["meta"]
            if not meta.get("more"):
                break
            offset += meta["count"]
        return objects

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
