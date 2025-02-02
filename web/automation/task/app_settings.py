from sqlalchemy.orm import Session

from web.database.model import AppSettings

from ..syncer import Syncer


class AppSettingSyncer(Syncer):
    @classmethod
    def run(cls, s: Session) -> None:
        if s.query(AppSettings).count() == 0:
            s.add(AppSettings())
