from flask_login import current_user
from sqlalchemy.orm import Session

from webshop.database.client import conn
from webshop.database.model import Cart


def get_resource(cart_id: int) -> dict:
    with conn.begin() as s:
        cart = s.query(Cart).filter_by(id=cart_id).first()
        return _build(s, cart)


def _build(s: Session, cart: Cart) -> dict:
    return {
        "id": cart.id,
        "shipping_id": cart.shipping_id,
        "billing_id": cart.billing_id,
        "cart_count": current_user.cart_count,
        "subtotal_price_vat": cart.subtotal_price_vat,
        "shipment_price_vat": cart.shipment_price_vat,
        "discount_price_vat": cart.discount_price_vat,
        "total_price_vat": cart.total_price_vat,
        "currency_code": cart.currency.code,
    }
