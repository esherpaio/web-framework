from datetime import datetime, timedelta, timezone

from sqlalchemy.sql import not_, true

from web.database import conn
from web.database.model import Billing, Shipping, User

from ..automator import Cleaner


class UserCleaner(Cleaner):
    @classmethod
    def run(cls, days: int = 14) -> None:
        cls.log_start()
        with conn.begin() as s:
            before_dt = datetime.now(timezone.utc) - timedelta(days=days)
            s.query(User).filter(
                User.created_at <= before_dt,
                User.is_guest == true(),
                not_(User.carts.any()),
                not_(User.orders.any()),
                not_(s.query(Billing).filter(Billing.user_id == User.id).exists()),
                not_(s.query(Shipping).filter(Shipping.user_id == User.id).exists()),
            ).delete()
