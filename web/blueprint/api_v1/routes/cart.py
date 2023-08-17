from typing import Any

from flask import abort
from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.client import conn
from web.database.model import Cart, Coupon, ShipmentMethod
from web.helper.api import ApiText, response
from web.helper.cart import get_vat
from web.helper.localization import current_locale

#
# Configuration
#


class CartAPI(API):
    model = Cart
    patch_columns = {
        Cart.billing_id,
        Cart.shipping_id,
        Cart.coupon_id,
        Cart.shipment_method_id,
        "coupon_code",
    }
    get_columns = {
        Cart.id,
        Cart.billing_id,
        Cart.shipping_id,
        Cart.coupon_id,
        Cart.currency_id,
        Cart.shipment_method_id,
        Cart.vat_rate,
        Cart.vat_reverse,
        "items_count",
        "subtotal_price_vat",
        "discount_price_vat",
        "shipment_price_vat",
        "total_price_vat",
    }


#
# Endpoints
#


@api_v1_bp.post("/carts")
def post_carts() -> Response:
    api = CartAPI()
    data: dict[str, Any] = {}
    with conn.begin() as s:
        model = api.model()
        set_user(s, data, model)
        set_currency(s, data, model)
        api.insert(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.get("/carts")
def get_carts() -> Response:
    api = CartAPI()
    with conn.begin() as s:
        filters = {Cart.user_id == current_user.id}
        models = api.list_(s, *filters, limit=1)
        resources = api.gen_resources(s, models)
    return response(data=resources)


@api_v1_bp.patch("/carts/<int:cart_id>")
def patch_carts_id(cart_id: int) -> Response:
    api = CartAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        filters = {Cart.user_id == current_user.id}
        model = api.get(s, cart_id, *filters)
        set_currency(s, data, model)
        set_shipment(s, data, model)
        set_coupon(s, data, model)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


#
# Functions
#


def set_user(s: Session, data: dict, cart: Cart) -> None:
    cart.user_id = current_user.id


def set_currency(s: Session, data: dict, cart: Cart) -> None:
    if cart.billing:
        country_code = cart.billing.country.code
        is_business = cart.billing.company is not None
        currency_id = cart.billing.country.currency_id
    else:
        country_code = current_locale.country.code
        is_business = False
        currency_id = current_locale.currency.id

    vat_rate, vat_reverse = get_vat(country_code, is_business)
    cart.currency_id = currency_id
    cart.vat_rate = vat_rate
    cart.vat_reverse = vat_reverse


def set_shipment(s: Session, data: dict, cart: Cart) -> None:
    shipment_method_id = data.get("shipment_method_id")
    if shipment_method_id is not None:
        shipment_method = (
            s.query(ShipmentMethod)
            .filter_by(id=shipment_method_id, is_deleted=False)
            .first()
        )
        if shipment_method is None:
            abort(response(400, ApiText.HTTP_400))
        shipment_price = shipment_method.unit_price * cart.currency.rate
        cart.shipment_method_id = shipment_method.id
        cart.shipment_price = shipment_price


def set_coupon(s: Session, data: dict, cart: Cart) -> None:
    coupon_code = data.get("coupon_code")
    if coupon_code is not None:
        coupon = s.query(Coupon).filter_by(code=coupon_code, is_deleted=False).first()
        if coupon is None:
            abort(response(400, ApiText.HTTP_400))
        cart.coupon_id = coupon.id
