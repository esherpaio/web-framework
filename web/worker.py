import sched
import time
from typing import Callable, Type

from web.automation import Automator
from web.config import config
from web.database import conn
from web.i18n import translator
from web.logger import log
from web.mail import MailEvent, mail


class Worker:
    def __init__(
        self,
        mail_events: dict[MailEvent | str, list[Callable]] | None = None,
        translations_dir: str | None = None,
        automation_tasks: list[Type[Automator]] | None = None,
    ) -> None:
        log.info("Initializing worker")

        self.setup_i18n(translations_dir)
        self.setup_mail(mail_events)

        self.scheduler = sched.scheduler(time.time, time.sleep)
        interval_s = config.WORKER_INTERVAL_S
        if not isinstance(interval_s, int):
            raise ValueError(f"Invalid interval {interval_s}")
        elif not 30 <= interval_s <= 3600:
            raise ValueError("Invalid must be between 30 and 3600 seconds")
        self.interval_s = interval_s
        if automation_tasks is None:
            automation_tasks = []
        self.tasks = automation_tasks

    #
    # Setup
    #

    def setup_i18n(self, dir_: str | None) -> None:
        if dir_ is None:
            return
        log.info(f"Loading translations from {dir_}")
        translator.load_dir(dir_)

    def setup_mail(self, events: dict[MailEvent | str, list[Callable]] | None) -> None:
        if config.EMAIL_METHOD:
            log.info(f"Configuring email method {config.EMAIL_METHOD}")
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
                log.info(f"Running task {task.__name__}")
                with conn.begin() as s:
                    task.run(s)
            except Exception as e:
                log.error(f"Error running task {task.__name__}: {e}")
        self.scheduler.enter(self.interval_s, 1, self._run)

    def start(self) -> None:
        self.scheduler.enter(0, 1, self._run)
        self.scheduler.run()
