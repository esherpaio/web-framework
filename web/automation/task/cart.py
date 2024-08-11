from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.sql import and_, or_

from web.database.model import Cart

from ..cleaner import Cleaner


class CartCleaner(Cleaner):
    MODEL = Cart

    @classmethod
    def run(cls, s: Session, days: int = 28) -> None:
        # Delete carts older than 30 days
        dt = datetime.utcnow() - timedelta(days=days)
        s.query(Cart).filter(
            or_(
                Cart.updated_at <= dt,
                and_(Cart.created_at <= dt, Cart.updated_at.is_(None)),
            )
        ).delete()
