from flask_login import current_user
from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import CartItem


def get_resource(cart_item_id: int) -> dict:
    with conn.begin() as s:
        cart_item = s.query(CartItem).filter_by(id=cart_item_id).first()
        return _build(s, cart_item)


def _build(s: Session, cart_item: CartItem) -> dict:
    return {
        "cart_id": cart_item.cart_id,
        "id": cart_item.id,
        "quantity": cart_item.quantity,
        "sku_id": cart_item.sku_id,
    }
