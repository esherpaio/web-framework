import time
from datetime import datetime, timezone
from threading import Thread
from typing import Callable

from web.database import conn
from web.database.model import AppSettings
from web.logger import log
from web.utils import Singleton


class CacheManager(metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self._updated_at: datetime = datetime.now(timezone.utc)
        self._active: bool = True
        self.hooks: list[Callable] = []
        self.update(force=True)

    def pause(self) -> None:
        if not self._active:
            log.info("Cache is already paused")
            return
        self._active = False

    def resume(self) -> None:
        if self._active:
            log.info("Cache is already active")
            return
        self._active = True

    def add_hook(self, hook: Callable) -> None:
        if hook not in self.hooks:
            self.hooks.append(hook)

    @property
    def expired(self) -> bool:
        if self._updated_at is None:
            return True
        with conn.begin() as s:
            settings = s.query(AppSettings).first()
        if not settings or settings.cached_at is None:
            return False
        return settings.cached_at > self._updated_at

    def update(self, force: bool = False) -> None:
        if not force:
            try:
                time.sleep(60)
            except Exception:
                return
        if self._active:
            Thread(target=self.update, daemon=True).start()
        if force or self.expired:
            log.info("Updating cache")
            self._updated_at = datetime.now(timezone.utc)
            for hook in self.hooks:
                hook()


cache_manager = CacheManager()
