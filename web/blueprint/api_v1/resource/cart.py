from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import Cart


def get_resource(cart_id: int) -> dict:
    with conn.begin() as s:
        cart = s.query(Cart).filter_by(id=cart_id).first()
        return _build(s, cart)


def _build(s: Session, cart: Cart) -> dict:
    return {
        "billing_id": cart.billing_id,
        "cart_count": cart.items_count,
        "coupon_id": cart.coupon_id,
        "currency_code": cart.currency.code,
        "discount_price_vat": cart.discount_price_vat,
        "id": cart.id,
        "shipment_method_id": cart.shipment_method_id,
        "shipment_price_vat": cart.shipment_price_vat,
        "shipping_id": cart.shipping_id,
        "subtotal_price_vat": cart.subtotal_price_vat,
        "total_price_vat": cart.total_price_vat,
        "vat_rate": cart.vat_rate,
        "vat_reverse": cart.vat_reverse,
    }
