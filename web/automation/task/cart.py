from datetime import datetime, timedelta, timezone

from sqlalchemy.sql import and_, or_

from web.database import conn
from web.database.model import Cart

from ..automator import Cleaner


class CartCleaner(Cleaner):
    @classmethod
    def run(cls, days: int = 28) -> None:
        cls.log_start()
        with conn.begin() as s:
            before_dt = datetime.now(timezone.utc) - timedelta(days=days)
            s.query(Cart).filter(
                or_(
                    Cart.updated_at <= before_dt,
                    and_(Cart.created_at <= before_dt, Cart.updated_at.is_(None)),
                )
            ).delete()
