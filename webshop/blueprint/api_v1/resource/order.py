from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import Order


def get_resource(order_id: int) -> dict:
    with Conn.begin() as s:
        order = s.query(Order).filter_by(id=order_id).first()
        return _build(s, order)


def _build(s: Session, order: Order) -> dict:
    return {
        "id": order.id,
    }
