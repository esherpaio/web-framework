from datetime import datetime, timedelta

from sqlalchemy.sql import not_, true

from web.database.client import conn
from web.database.model import User


def clean_users() -> None:
    """Script to clean up old users."""

    with conn.begin() as s:
        # Delete guests older than 7 days
        days_7 = datetime.utcnow() - timedelta(days=7)
        s.query(User).filter(
            User.created_at <= days_7,
            User.is_guest == true(),
            not_(User.carts.any()),
            not_(User.orders.any()),
        ).delete()


if __name__ == "__main__":
    clean_users()
