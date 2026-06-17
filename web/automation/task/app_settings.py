from web.database import conn
from web.database.model import AppSettings

from ..automator import SeedSyncer


class AppSettingSeedSyncer(SeedSyncer):
    INTERVAL_S = 86400

    @classmethod
    def run(cls) -> None:
        cls.log_start()
        with conn.begin() as s:
            if s.query(AppSettings).count() == 0:
                s.add(AppSettings())
