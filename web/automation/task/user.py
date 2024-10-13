from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy.sql import not_, true

from web.database.model import User

from ..cleaner import Cleaner


class UserCleaner(Cleaner):
    MODEL = User

    @classmethod
    def run(cls, s: Session, days: int = 14) -> None:
        # Delete guests older than x days
        dt = datetime.now(timezone.utc) - timedelta(days=days)
        s.query(cls.MODEL).filter(
            User.created_at <= dt,
            User.is_guest == true(),
            not_(User.carts.any()),
            not_(User.orders.any()),
            not_(User.billing),
            not_(User.shipping),
        ).delete()
