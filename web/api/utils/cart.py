from typing import Callable

from sqlalchemy import false, or_
from sqlalchemy.orm import Session
from werkzeug import Response

from web.auth import current_user
from web.database import conn
from web.database.model import (
    Billing,
    Cart,
    ShipmentClass,
    ShipmentMethod,
    ShipmentZone,
    Shipping,
    User,
)
from web.locale import current_locale


def predict_shipping(s: Session, cart: Cart) -> Shipping | None:
    """Get the most accurate shipping object."""
    # Get user
    if current_user and current_user.id:
        user = s.query(User).filter_by(id=current_user.id).first()
    else:
        user = None
    # Get shipping
    if cart and cart.shipping_id:
        shipping = s.query(Shipping).filter_by(id=cart.shipping_id).first()
    elif user and user.shipping_id:
        shipping = s.query(Shipping).filter_by(id=user.shipping_id).first()
    else:
        shipping = None
    return shipping


def predict_billing(s: Session, cart: Cart) -> Billing | None:
    """Get the most accurate billing object."""
    # Get user
    if current_user and current_user.id:
        user = s.query(User).filter_by(id=current_user.id).first()
    else:
        user = None
    # Get billing
    if cart and cart.billing_id:
        billing = s.query(Billing).filter_by(id=cart.billing_id).first()
    elif user and user.billing_id:
        billing = s.query(Billing).filter_by(id=user.billing_id).first()
    else:
        billing = None
    return billing


def get_shipment_methods(s: Session, cart: Cart) -> list[ShipmentMethod]:
    # Get all possible shipping class ids
    shipment_class_ids = []
    for item in cart.items:
        shipment_class_id = item.sku.product.shipment_class_id
        if shipment_class_id:
            shipment_class_ids.append(shipment_class_id)
    # Determine the shipping class
    shipment_class = (
        s.query(ShipmentClass)
        .filter(
            ShipmentClass.id.in_(shipment_class_ids),
            ShipmentClass.is_deleted == false(),
        )
        .order_by(ShipmentClass.order)
        .first()
    )
    # Get country_id and region_id
    if cart.shipping:
        country_id = cart.shipping.country_id
        region_id = cart.shipping.country.region_id
    else:
        country_id = current_locale.country.id
        region_id = current_locale.country.region_id
    # Determine the shipping zone
    shipment_zone = (
        s.query(ShipmentZone)
        .filter(
            or_(
                ShipmentZone.country_id == country_id,
                ShipmentZone.region_id == region_id,
            ),
            ShipmentZone.is_deleted == false(),
        )
        .order_by(ShipmentZone.order)
        .first()
    )
    # Get shipment methods
    if shipment_zone and shipment_class:
        shipment_methods = (
            s.query(ShipmentMethod)
            .filter_by(
                class_id=shipment_class.id,
                zone_id=shipment_zone.id,
                is_deleted=False,
            )
            .order_by(ShipmentMethod.unit_price)
            .all()
        )
    else:
        shipment_methods = []
    return shipment_methods


def transfer_cart(f: Callable) -> Callable[..., Response]:
    """Transfer a cart from one session to another."""

    def wrap(*args, **kwargs) -> Response:
        with conn.begin() as s:
            if not current_user:
                return f(*args, **kwargs)
            # Get before and after user ids
            prev_user_id = current_user.id
            resp = f(*args, **kwargs)
            curr_user_id = current_user.id
            # Transfer cart
            prev_cart = s.query(Cart).filter_by(user_id=prev_user_id).first()
            if prev_cart is not None:
                s.query(Cart).filter_by(user_id=curr_user_id).delete()
                prev_cart.user_id = curr_user_id
                s.flush()

        return resp

    wrap.__name__ = f.__name__
    return wrap
