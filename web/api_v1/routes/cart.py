from flask import Response

from web.api_v1 import api_v1_bp
from web.api_v1.resource.cart import get_resource
from web.database.client import conn
from web.database.model import Cart, Coupon, ShipmentMethod
from web.helper.api import ApiText, json_get, response
from web.helper.cart import get_vat
from web.helper.localization import current_locale
from web.helper.user import get_access


@api_v1_bp.post("/carts")
def post_carts() -> Response:
    with conn.begin() as s:
        # Authorize request
        # Get or insert cart
        access = get_access(s)
        cart = s.query(Cart).filter_by(access_id=access.id).first()
        if not cart:
            country_code = current_locale.country.code
            vat_rate, vat_reverse = get_vat(country_code, is_business=False)
            cart = Cart(
                access_id=access.id,
                currency_id=current_locale.currency.id,
                vat_rate=vat_rate,
                vat_reverse=vat_reverse,
            )
            s.add(cart)
            s.flush()

    resource = get_resource(cart.id)
    return response(data=resource)


@api_v1_bp.get("/carts")
def get_carts() -> Response:
    with conn.begin() as s:
        # Authorize request
        # Get cart
        # Raise if cart doesn't exist
        access = get_access(s)
        cart = s.query(Cart).filter_by(access_id=access.id).first()
        if not cart:
            return response(404, ApiText.HTTP_404)

    resource = [get_resource(cart.id)]
    return response(data=resource)


@api_v1_bp.patch("/carts/<int:cart_id>")
def patch_carts_id(cart_id: int) -> Response:
    billing_id, has_billing_id = json_get("billing_id", int)
    coupon_code, has_coupon_code = json_get("coupon_code", str)
    shipment_method_id, has_shipment_method_id = json_get("shipment_method_id", int)
    shipping_id, has_shipping_id = json_get("shipping_id", int)

    with conn.begin() as s:
        # Authorize request
        # Get cart
        # Raise if cart doesn't exist
        access = get_access(s)
        cart = s.query(Cart).filter_by(access_id=access.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Update shipping_id
        if has_shipping_id:
            cart.shipping_id = shipping_id
            s.flush()
        # Update billing_id
        if has_billing_id:
            cart.billing_id = billing_id
            s.flush()
        # Sync currency_id, vat_rate and vat_reverse
        if cart.billing:
            country_code = cart.billing.country.code
            is_business = cart.billing.company is not None
            vat_rate, vat_reverse = get_vat(country_code, is_business)
            cart.currency_id = cart.billing.country.currency_id
            cart.vat_rate = vat_rate
            cart.vat_reverse = vat_reverse
            s.flush()
        # Update shipment_method_id and shipment_price
        if cart.shipping_id and has_shipment_method_id:
            shipment_method = (
                s.query(ShipmentMethod)
                .filter_by(id=shipment_method_id, is_deleted=False)
                .first()
            )
            cart.shipment_method_id = shipment_method.id
            cart.shipment_price = shipment_method.unit_price * cart.currency.rate
            s.flush()
        # Update coupon_id
        if has_coupon_code:
            coupon = (
                s.query(Coupon).filter_by(code=coupon_code, is_deleted=False).first()
            )
            coupon_id = coupon.id if coupon else None
            cart.coupon_id = coupon_id
            s.flush()

    resource = get_resource(cart_id)
    return response(data=resource)
