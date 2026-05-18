import atexit
from datetime import datetime, timezone
from threading import Event, Thread
from typing import Callable

from web.database import conn
from web.database.model import AppSettings
from web.logger import log
from web.utils import Singleton

REFRESH_INTERVAL_S = 60
SHUTDOWN_TIMEOUT_S = 5


class CacheManager(metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self._updated_at: datetime = datetime.now(timezone.utc)
        self._active: bool = True
        self._stop: Event = Event()
        self._thread: Thread | None = None
        self.hooks: list[Callable] = []
        self.update(force=True)
        self._start_loop()

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
        if not (force or (self._active and self.expired)):
            return
        log.info("Updating cache")
        self._updated_at = datetime.now(timezone.utc)
        for hook in self.hooks:
            try:
                hook()
            except Exception as e:
                log.error(f"Error running cache hook {hook.__name__}: {e}")

    def _start_loop(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = Thread(
            target=self._refresh_loop,
            name="CacheManagerRefresh",
            daemon=False,
        )
        self._thread.start()
        atexit.register(self._shutdown)

    def _refresh_loop(self) -> None:
        while not self._stop.wait(REFRESH_INTERVAL_S):
            try:
                self.update()
            except Exception as e:
                log.error(f"Error refreshing cache: {e}")

    def _shutdown(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=SHUTDOWN_TIMEOUT_S)


cache_manager = CacheManager()
