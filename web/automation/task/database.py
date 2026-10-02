import time

from alembic import command
from alembic.config import Config

from web.database import create_database, get_revisions
from web.logger import log

from ..automator import Automator


class DatabaseRevisionCheck(Automator):
    @classmethod
    def run(cls, migrate: bool = False) -> None:
        if migrate:
            create_database()

        current, expected = get_revisions()
        if current == expected:
            return

        if migrate:
            log.info(f"Migrating database from {current} to {expected}")
            command.upgrade(Config("alembic.ini"), "head")
            log.info("Database migrated; exiting to restart")
        else:
            log.warning(
                f"Database revision mismatch: current={current}, "
                f"expected={expected}; exiting to restart"
            )
            time.sleep(10)
        raise SystemExit(0)
