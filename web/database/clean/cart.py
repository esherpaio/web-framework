from datetime import datetime, timedelta

from sqlalchemy.sql import and_, or_

from .. import conn
from ..model import Cart


def clean_carts() -> None:
    """Script to clean up old carts."""

    with conn.begin() as s:
        # Delete carts older than 30 days
        days = datetime.utcnow() - timedelta(days=30)
        s.query(Cart).filter(
            or_(
                Cart.updated_at <= days,
                and_(Cart.created_at <= days, Cart.updated_at.is_(None)),
            )
        ).delete()


if __name__ == "__main__":
    clean_carts()
