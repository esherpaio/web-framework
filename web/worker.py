import os
import sched
import signal
import time
from typing import Callable, Type

from web.automation import Automator
from web.i18n import translator
from web.logger import log
from web.mail import MailEvent, mail
from web.setup import settings


class Worker:
    def __init__(
        self,
        start_delay_s: int = 30,
        mail_events: dict[MailEvent | str, list[Callable]] | None = None,
        translations_dir: str | None = None,
        automation_tasks: list[Type[Automator]] | None = None,
    ) -> None:
        log.info("Initializing worker")
        self.start_delay_s = start_delay_s
        self.interval_s = settings.WORKER_INTERVAL_S

        self.setup_i18n(translations_dir)
        self.setup_mail(mail_events)

        if automation_tasks is None:
            automation_tasks = []
        self.tasks = automation_tasks

        self.scheduler = sched.scheduler(time.time, time.sleep)
        signal.signal(signal.SIGTERM, self._signal_exit)
        signal.signal(signal.SIGINT, self._signal_exit)

    def _signal_exit(self, signum, *args) -> None:
        log.info(f"Worker received signal {signum}")
        self.stop()

    #
    # Setup
    #

    def setup_i18n(self, dir_: str | None) -> None:
        if dir_ is None:
            return
        log.info(f"Loading translations from {dir_}")
        translator.load_dir(dir_)

    def setup_mail(self, events: dict[MailEvent | str, list[Callable]] | None) -> None:
        if settings.MAIL_METHOD:
            log.info(f"Configuring email method {settings.MAIL_METHOD}")
        else:
            log.warning("No email method configured")

        if events:
            log.info(f"Updating {len(events)} mail events")
            mail.events.update(events)

    #
    # Loop
    #

    def _run(self) -> None:
        for task in self.tasks:
            try:
                task.run()
            except Exception as e:
                log.error(f"Error running task {task.__name__}: {e}")
        self.scheduler.enter(delay=self.interval_s, priority=1, action=self._run)

    def start(self) -> None:
        self.scheduler.enter(delay=self.start_delay_s, priority=1, action=self._run)
        try:
            self.scheduler.run()
        except (KeyboardInterrupt, SystemExit):
            log.info("Worker stopped gracefully")
            os._exit(1)

    def stop(self) -> None:
        for event in list(self.scheduler.queue):
            try:
                self.scheduler.cancel(event)
            except ValueError:
                pass
        raise SystemExit(0)
