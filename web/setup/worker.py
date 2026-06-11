import atexit
import signal
import time
from threading import Event, Thread
from types import FrameType
from typing import Callable, Type

from flask import Flask

from web.automation import Automator
from web.cache import cache_common, cache_manager
from web.i18n import translator
from web.logger import log
from web.mail import MailEvent, mail
from web.setup import config
from web.setup.logging import patch_logging

SHUTDOWN_TIMEOUT_S = 5


class Worker:
    def __init__(self) -> None:
        log.info("Initializing worker")
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._tasks: list[Type[Automator]] = []
        self._interval_s = config.WORKER_INTERVAL_S
        self._last_loop: float | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        log.info("Starting worker")
        self._stop_event.clear()
        atexit.register(self._on_shutdown)
        self._on_sigint()
        self._thread = Thread(
            target=self._schedule,
            name="Worker",
            daemon=False,
        )
        self._thread.start()

    #
    # Setup
    #

    def setup_logging(self) -> None:
        patch_logging()

    def setup_i18n(self, dir_: str | None) -> None:
        if dir_ is None:
            return
        log.info(f"Loading translations from {dir_}")
        translator.load_dir(dir_)

    def setup_cache(self, hook: Callable | None = None) -> None:
        cache_manager.add_hook(cache_common)
        if hook is not None:
            cache_manager.add_hook(hook)
        cache_manager.update(force=True)

    def setup_mail(self, events: dict[MailEvent | str, list[Callable]] | None) -> None:
        if config.MAIL_METHOD:
            log.info(f"Configuring email method {config.MAIL_METHOD}")
        else:
            log.warning("No email method configured")

        if events:
            log.info(f"Updating {len(events)} mail events")
            mail.events.update(events)

    def setup_flask(self, app: Flask) -> None:
        app.add_url_rule("/", endpoint="home", view_func=lambda: "OK")

    def setup_tasks(self, tasks: list[Type[Automator]]) -> None:
        if not tasks:
            log.warning("No automation tasks configured")
            return

        log.info(f"Adding {len(tasks)} automation tasks")
        self._tasks = tasks

    #
    # Private
    #

    def _schedule(self) -> None:
        while not self._stop_event.is_set():
            if (
                self._last_loop is None
                or self._last_loop + self._interval_s <= time.monotonic()
            ):
                self._last_loop = time.monotonic()
                self._loop()
            else:
                self._stop_event.wait(self._interval_s)

    def _loop(self) -> None:
        for task in self._tasks:
            if self._stop_event.is_set():
                return
            task_cls = task()
            if config.DEBUG and not task_cls.RUN_DEBUG:
                log.debug(f"Skipping task {task_cls} in debug mode")
                continue
            if not task_cls.should_run():
                log.debug(f"Skipping task {task_cls} while interval not reached")
                continue
            try:
                task_cls.run()
            except Exception as e:
                log.error(f"Error running task {task_cls}: {e}")
            task_cls.mark_run()

    def _on_shutdown(self) -> None:
        log.info("Stopping worker")
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=SHUTDOWN_TIMEOUT_S)

    def _on_sigint(self) -> None:
        prev = signal.getsignal(signal.SIGINT)

        def handler(sig: int, frame: FrameType | None) -> None:
            self._stop_event.set()
            signal.signal(signal.SIGINT, prev)
            if callable(prev):
                prev(sig, frame)

        signal.signal(signal.SIGINT, handler)
