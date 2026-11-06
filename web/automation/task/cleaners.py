from datetime import datetime, timedelta, timezone

from sqlalchemy.sql import and_, not_, or_, true

from web.database import conn
from web.database.model import Billing, Cart, Email, EmailType, Shipping, User

from ..automator import Cleaner


class CartCleaner(Cleaner):
    INTERVAL_S = 86400

    @classmethod
    def run(cls, days: int = 28) -> None:
        with conn.begin() as s:
            before_dt = datetime.now(timezone.utc) - timedelta(days=days)
            s.query(Cart).filter(
                or_(
                    Cart.updated_at <= before_dt,
                    and_(Cart.created_at <= before_dt, Cart.updated_at.is_(None)),
                )
            ).delete()


class EmailCleaner(Cleaner):
    INTERVAL_S = 86400

    @classmethod
    def run(cls) -> None:
        before = datetime.now(timezone.utc) - timedelta(days=30)
        with conn.begin() as s:
            s.query(Email).filter(
                Email.type != EmailType.OK,
                Email.created_at < before,
            ).delete()


class UserCleaner(Cleaner):
    INTERVAL_S = 86400

    @classmethod
    def run(cls, days: int = 14) -> None:
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
