from sqlalchemy.orm import Session

from web.database.model import AppSetting

from ..syncer import Syncer


class AppSettingSyncer(Syncer):
    @classmethod
    def run(cls, s: Session) -> None:
        if s.query(AppSetting).count() == 0:
            s.add(AppSetting())
