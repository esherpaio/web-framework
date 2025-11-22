import logging
import os
import signal
import time
from threading import Event, Thread
from types import FrameType
from typing import Callable, Type

from flask import Flask

from web.automation import Automator
from web.i18n import translator
from web.logger import WerkzeugFilter, log
from web.mail import MailEvent, mail
from web.setup import config
from web.setup.logging import patch_logging


class Worker:
    def __init__(self) -> None:
        log.info("Initializing worker")
        self._thread: Thread | None = None
        self._stop_event = Event()
        self._tasks: list[Type[Automator]] = []
        self._interval_s = config.WORKER_INTERVAL_S
        self._last_event_time: float | None = None

        signal.signal(signal.SIGTERM, self._signal)
        signal.signal(signal.SIGINT, self._signal)

    def _signal(self, signum: int, frame: FrameType | None) -> None:
        log.info(f"Worker received signal {signum}")
        self.stop()

    #
    # Setup
    #

    def setup_logging(self) -> None:
        patch_logging()
        log_werkzeug = logging.getLogger("werkzeug")
        log_werkzeug.addFilter(WerkzeugFilter())

    def setup_i18n(self, dir_: str | None) -> None:
        if dir_ is None:
            return
        log.info(f"Loading translations from {dir_}")
        translator.load_dir(dir_)

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
    # Worker
    #

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            log.warning("Worker is already running")
            return

        log.info("Starting worker")
        self._stop_event.clear()
        self._thread = Thread(target=self._start_scheduler)
        self._thread.start()

    def _start_scheduler(self) -> None:
        while not self._stop_event.is_set():
            current_time = time.monotonic()
            if (
                self._last_event_time is None
                or self._last_event_time + self._interval_s <= current_time
            ):
                self._last_event_time = time.monotonic()
                self._iterate_tasks()
            else:
                self._stop_event.wait(self._interval_s)

    def _iterate_tasks(self) -> None:
        for task in self._tasks:
            if self._stop_event.is_set():
                return
            try:
                task.run()
            except Exception as e:
                log.error(f"Error running task {task.__name__}: {e}")

    def stop(self) -> None:
        log.info("Stopping worker")
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5)
        os._exit(1)
