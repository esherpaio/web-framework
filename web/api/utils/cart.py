from sqlalchemy.orm import Session

from web.auth import current_user
from web.database.model import Billing, Cart, ShipmentMethod, Shipping, User
from web.locale import current_locale

from .shipment import select_shipment_methods


def predict_shipping(s: Session, cart: Cart) -> Shipping | None:
    """Get the most probable shipping object."""
    # Get user
    if current_user and current_user.id:
        user = s.query(User).filter_by(id=current_user.id).first()
    else:
        user = None
    # Get shipping
    if cart and cart.shipping_id:
        shipping = s.query(Shipping).filter_by(id=cart.shipping_id).first()
    elif user is not None:
        shipping = s.query(Shipping).filter_by(user_id=user.id, is_default=True).first()
    else:
        shipping = None
    return shipping


def predict_billing(s: Session, cart: Cart) -> Billing | None:
    """Get the most probable billing object."""
    # Get user
    if current_user and current_user.id:
        user = s.query(User).filter_by(id=current_user.id).first()
    else:
        user = None
    # Get billing
    if cart and cart.billing_id:
        billing = s.query(Billing).filter_by(id=cart.billing_id).first()
    elif user is not None:
        billing = s.query(Billing).filter_by(user_id=user.id, is_default=True).first()
    else:
        billing = None
    return billing


def get_shipment_methods_by_cart(s: Session, cart: Cart) -> list[ShipmentMethod]:
    class_ids = [
        item.sku.product.shipment_class_id
        for item in cart.items
        if item.sku.product.shipment_class_id is not None
    ]
    if cart.shipping:
        country = cart.shipping.country
    else:
        country = current_locale.country
    return select_shipment_methods(s, class_ids, country)
