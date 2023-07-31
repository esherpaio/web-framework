from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Cart, Coupon, ShipmentMethod
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


def set_currency(s: Session, data: dict, cart: Cart) -> None:
    if cart.billing is not None:
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
    if cart.shipping_id and shipment_method_id:
        shipment_method = (
            s.query(ShipmentMethod)
            .filter_by(id=shipment_method_id, is_deleted=False)
            .first()
        )
        if shipment_method is not None:
            cart.shipment_method_id = shipment_method.id
            cart.shipment_price = shipment_method.unit_price * cart.currency.rate


def set_coupon(s: Session, data: dict, cart: Cart) -> None:
    coupon_code = data.get("coupon_code")
    if coupon_code:
        coupon = s.query(Coupon).filter_by(code=coupon_code, is_deleted=False).first()
        if coupon is not None:
            cart.coupon_id = coupon.id


#
# Endpoints
#


@api_v1_bp.post("/carts")
def post_carts() -> Response:
    api = CartAPI()
    return api.post(
        add_request={"user_id": current_user.id},
        pre_calls=[set_currency],
    )


@api_v1_bp.get("/carts")
def get_carts() -> Response:
    api = CartAPI()
    return api.get(
        filters={Cart.user_id == current_user.id},
        as_list=True,
        max_size=1,
    )


@api_v1_bp.patch("/carts/<int:cart_id>")
def patch_carts_id(cart_id: int) -> Response:
    api = CartAPI()
    return api.patch(
        cart_id,
        filters={Cart.user_id == current_user.id},
        post_calls=[set_currency, set_shipment, set_coupon],
    )
