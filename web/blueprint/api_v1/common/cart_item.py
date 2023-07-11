from sqlalchemy.orm import Session

from web.database.model import Cart
from web.helper.cart import get_shipment_methods


def update_cart_shipment_methods(s: Session, cart: Cart) -> None:
    shipment_methods = get_shipment_methods(s, cart)
    if shipment_methods:
        shipment_method = min(shipment_methods)
        cart.shipment_method_id = shipment_method.id
        cart.shipment_price = shipment_method.unit_price * cart.currency.rate
    else:
        cart.shipment_method_id = None
        cart.shipment_price = 0
    s.flush()
