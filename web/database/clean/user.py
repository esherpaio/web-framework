from datetime import datetime, timedelta

from sqlalchemy.sql import not_, true

from ..client import conn
from ..model import User


def clean_users() -> None:
    """Script to clean up old users."""

    with conn.begin() as s:
        # Delete guests older than 14 days
        days = datetime.utcnow() - timedelta(days=14)
        s.query(User).filter(
            User.created_at <= days,
            User.is_guest == true(),
            not_(User.carts.any()),
            not_(User.orders.any()),
            not_(User.billing),
            not_(User.shipping),
        ).delete()


if __name__ == "__main__":
    clean_users()
