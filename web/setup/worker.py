import logging
import sched
import signal
import time
from threading import Event, Thread
from types import FrameType
from typing import Callable, Type

from web.automation import Automator
from web.i18n import translator
from web.logger import WerkzeugFilter, log
from web.mail import MailEvent, mail
from web.setup import config


class Worker:
    def __init__(self, start_delay_s: int = 0, stop_timeout_s: int = 5) -> None:
        log.info("Initializing worker")
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._thread: Thread | None = None
        self._stop_event = Event()
        self._tasks: list[Type[Automator]] = []
        self._start_delay_s = start_delay_s
        self._stop_timeout_s = stop_timeout_s
        self._interval_s = config.WORKER_INTERVAL_S

        signal.signal(signal.SIGTERM, self._signal)
        signal.signal(signal.SIGINT, self._signal)

    def _signal(self, signum: int, frame: FrameType | None) -> None:
        log.info(f"Worker received signal {signum}")
        self.stop()

    #
    # Setup
    #

    def setup_logging(self) -> None:
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
        self._thread = Thread(target=self._run_scheduler, daemon=True)
        self._thread.start()

    def _run_scheduler(self) -> None:
        self._scheduler.enter(delay=self._start_delay_s, priority=1, action=self._run)
        self._scheduler.run()

    def _run(self) -> None:
        for task in self._tasks:
            try:
                task.run()
            except Exception as e:
                log.error(f"Error running task {task.__name__}: {e}")

        if self._stop_event.is_set():
            return
        self._scheduler.enter(delay=self._interval_s, priority=1, action=self._run)

    def stop(self) -> None:
        log.info("Stopping worker")
        self._stop_event.set()

        for event in list(self._scheduler.queue):
            try:
                self._scheduler.cancel(event)
            except ValueError:
                pass

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=self._stop_timeout_s)
            if self._thread.is_alive():
                log.warning("Worker thread did not stop within timeout")
