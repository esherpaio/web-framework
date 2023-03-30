from flask_login import current_user
from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import CartItem


def get_resource(cart_item_id: int) -> dict:
    with Conn.begin() as s:
        cart_item = s.query(CartItem).filter_by(id=cart_item_id).first()
        return _build(s, cart_item)


def _build(s: Session, cart_item: CartItem) -> dict:
    return {
        "cart_count": current_user.cart_count,
    }
