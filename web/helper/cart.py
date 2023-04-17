from datetime import datetime
from typing import Callable

import pyvat
from flask import Response
from flask_login import current_user
from pyvat import ItemType, Party, VatChargeAction
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false

from web import config
from web.database.client import conn
from web.database.model import Cart, ShipmentMethod, ShipmentClass, ShipmentZone
from web.database.model import Shipping, Billing, User
from web.helper.security import get_access


def transfer_cart(
    f: Callable,
) -> Callable[..., Response]:
    """Transfer a cart from one session to another.

    To be used as a decorator on a login-endpoint.
    """

    def wrap(*args, **kwargs) -> Response:
        with conn.begin() as s:
            # Get before and after access objects
            prev_access = get_access(s)
            resp = f(*args, **kwargs)
            curr_access = get_access(s)

            # Transfer cart
            prev_cart = s.query(Cart).filter_by(access_id=prev_access.id).first()
            if prev_cart:
                s.query(Cart).filter_by(access_id=curr_access.id).delete()
                prev_cart.access_id = curr_access.id

                # Update cart count
                update_cart_count(s, prev_cart)

        return resp

    wrap.__name__ = f.__name__
    return wrap


def predict_cart_info(
    s: Session,
    cart: Cart,
) -> tuple[Shipping | None, Billing | None]:
    """Predict the most accurate shipping and billing objects.

    In the following order: cart -> user -> None.
    This is useful for pre-filling forms on a frontend.
    """

    if current_user.is_authenticated:
        user = s.query(User).filter_by(id=current_user.id).first()
    else:
        user = None

    if cart and cart.shipping_id:
        shipping = s.query(Shipping).filter_by(id=cart.shipping_id).first()
    elif user and user.shipping_id:
        shipping = s.query(Shipping).filter_by(id=user.shipping_id).first()
    else:
        shipping = None

    if cart and cart.billing_id:
        billing = s.query(Billing).filter_by(id=cart.billing_id).first()
    elif user and user.billing_id:
        billing = s.query(Billing).filter_by(id=user.billing_id).first()
    else:
        billing = None

    return shipping, billing


def get_shipment_methods(
    s: Session,
    cart: Cart,
) -> list[ShipmentMethod]:
    """Generate a list of shipment methods."""

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
        country_id = current_user.country.id
        region_id = current_user.country.region_id

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


def get_vat(
    country_code: str,
    is_business: bool,
) -> tuple[float, bool]:
    """Calculate a VAT rate and determine whether it's reversed."""

    date = datetime.utcnow().date()
    type_ = ItemType.generic_electronic_service
    buyer = Party(country_code, is_business)
    seller = Party(config.BUSINESS_COUNTRY_CODE, True)

    vat = pyvat.get_sale_vat_charge(date, type_, buyer, seller)
    if vat.action == VatChargeAction.charge:
        vat_rate = int(vat.rate) / 100 + 1
        vat_reverse = False
    else:
        vat_rate = 1
        vat_reverse = True

    return vat_rate, vat_reverse


def update_cart_count(
    s: Session,
    cart: Cart | None = None,
) -> int:
    """Update the cart count in the session."""

    if cart:
        cart_count = len(cart.items)
    else:
        cart_count = 0
    current_user.cart_count = cart_count
    return cart_count
