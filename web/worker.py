import sched
import time
from typing import Type

from web.automation import Automator
from web.config import config
from web.database import conn
from web.logger import log


class Worker:
    TASKS: list[Type[Automator]] = []

    def __init__(self, interval: int = 300) -> None:
        log.info("Initializing worker")
        self.scheduler = sched.scheduler(time.time, time.sleep)
        interval = config.WORKER_INTERVAL_S
        if not isinstance(interval, int):
            raise ValueError(f"Invalid interval {interval}")
        elif not 30 < interval < 3600:
            raise ValueError("Invalid must be between 30 and 3600 seconds")
        self.interval = interval
        self.set_tasks()

    def set_tasks(self) -> None:
        from web.automation.task import EmailWorker

        self.TASKS = [EmailWorker]

    def job(self) -> None:
        for task in self.TASKS:
            try:
                log.info(f"Running task {task.__name__}")
                with conn.begin() as s:
                    task.run(s)
            except Exception as e:
                log.error(f"Error running task {task.__name__}: {e}", exc_info=True)
        self.scheduler.enter(self.interval, 1, self.job)

    def start(self) -> None:
        self.scheduler.enter(0, 1, self.job)
        self.scheduler.run()


if __name__ == "__main__":
    worker = Worker()
    worker.start()
