from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import Order


def get_resource(order_id: int) -> dict:
    with conn.begin() as s:
        order = s.query(Order).filter_by(id=order_id).first()
        return _build(s, order)


def _build(s: Session, order: Order) -> dict:
    return {
        "id": order.id,
    }
