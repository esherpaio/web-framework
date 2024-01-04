from datetime import UTC, datetime, timedelta

from sqlalchemy.sql import and_, or_

from web.database.client import conn
from web.database.model import Cart


def clean_carts() -> None:
    """Script to clean up old carts."""

    with conn.begin() as s:
        # Delete carts older than 30 days
        days = datetime.now(UTC) - timedelta(days=30)
        s.query(Cart).filter(
            or_(
                Cart.updated_at <= days,
                and_(Cart.created_at <= days, Cart.updated_at.is_(None)),
            )
        ).delete()


if __name__ == "__main__":
    clean_carts()
