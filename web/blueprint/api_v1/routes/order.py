from enum import StrEnum

from flask import abort, g
from flask_login import current_user
from pyvat import is_vat_number_format_valid
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.blueprint.api_v1._common import create_refund
from web.database.client import conn
from web.database.model import Cart, Order, OrderLine, OrderStatusId, UserRoleLevel
from web.helper.api import ApiText, response
from web.helper.cart import get_shipment_methods
from web.helper.mollie_api import Mollie
from web.helper.user import access_control
from web.i18n.base import _
from web.mail.routes.order import send_order_received

#
# Configuration
#


class Text(StrEnum):
    PHONE_REQUIRED = _("API_ORDER_PHONE_REQUIRED")
    VAT_INVALID = _("API_ORDER_VAT_INVALID")
    VAT_NO_CONNECTION = _("API_ORDER_VAT_NO_CONNECTION")
    VAT_REQUIRED = _("API_ORDER_VAT_REQUIRED")


class OrderAPI(API):
    model = Order
    post_columns = {
        "cart_id",
    }
    get_columns = {
        Order.id,
    }


#
# Endpoints
#


@api_v1_bp.post("/orders")
def post_orders() -> Response:
    api = OrderAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        get_cart(s, data)
        val_cart(s, data)
        order = api.model()
        set_order(s, data, order)
        api.insert(s, data, order)
        set_order_lines(s, data, order)
        mail_order(s, data, order)
        resource = api.gen_resource(s, order)
    return response(data=resource)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/orders/<int:order_id>")
def delete_orders_id(order_id: int) -> Response:
    api = OrderAPI()
    data = api.gen_view_args_data()
    with conn.begin() as s:
        order = api.get(s, order_id)
        cancel_mollie(s, data, order)
    return response()


#
# Functions
#


def get_cart(s: Session, data: dict, *args) -> None:
    cart_id = data["cart_id"]
    filters = {Cart.id == cart_id, Cart.user_id == current_user.id}
    cart = s.query(Cart).filter(*filters).first()
    if cart is None:
        abort(response(404, ApiText.HTTP_404))
    g.cart = cart


def val_cart(s: Session, data: dict, *args) -> None:
    cart = g.cart

    # Check shipment method
    shipment_methods = get_shipment_methods(s, cart)
    if shipment_methods is not None:
        if cart.shipment_method_id is None:
            abort(response(400, ApiText.HTTP_400))

    # Check for valid shipment method
    shipment_method_ids = {x.id for x in shipment_methods}
    if cart.shipment_method_id is not None:
        if cart.shipment_method_id not in shipment_method_ids:
            abort(response(400, ApiText.HTTP_400))

    # Check phone required
    if cart.shipment_method is not None:
        if cart.shipment_method.phone_required:
            if cart.billing.phone is None:
                abort(response(400, Text.PHONE_REQUIRED))

    # Check VAT required in Europe
    if cart.billing.company is not None:
        if cart.billing.country.region.is_europe:
            if cart.billing.vat is None:
                abort(response(400, Text.VAT_REQUIRED))

    # Check VAT number
    if cart.billing.vat is not None:
        vat_parsed = "".join(x for x in cart.billing.vat if x.isalnum())
        is_valid = is_vat_number_format_valid(vat_parsed, cart.billing.country.code)
        if not is_valid:
            abort(response(400, Text.VAT_INVALID))


def set_order(s: Session, data: dict, order: Order) -> None:
    cart = g.cart

    if cart.coupon is not None:
        order.coupon_amount = cart.coupon.amount
        order.coupon_code = cart.coupon.code
        order.coupon_rate = cart.coupon.rate
    if cart.shipment_method is not None:
        order.shipment_name = cart.shipment_method.name
    order.billing_id = cart.billing_id
    order.currency_id = cart.currency_id
    order.shipment_price = cart.shipment_price
    order.shipping_id = cart.shipping_id
    order.total_price = cart.total_price
    order.vat_rate = cart.vat_rate
    order.vat_reverse = cart.vat_reverse
    order.user_id = current_user.id
    order.status_id = OrderStatusId.PENDING


def set_order_lines(s: Session, data: dict, order: Order) -> None:
    cart = g.cart
    order_lines = []

    for cart_item in cart.items:
        order_line = OrderLine()
        order_line.order_id = order.id
        order_line.sku_id = cart_item.sku_id
        order_line.quantity = cart_item.quantity
        order_line.total_price = cart_item.total_price
        order_lines.append(order_line)

    s.add_all(order_lines)
    s.flush()
    g.order_lines = order_lines


def mail_order(s: Session, data: dict, order: Order) -> None:
    send_order_received(
        order_id=order.id,
        billing_email=order.billing.email,
        shipping_email=order.shipping.email,
    )


def cancel_mollie(s: Session, data: dict, order: Order) -> None:
    # Try to cancel the Mollie payment
    mollie = Mollie().payments.get(order.mollie_id)
    if mollie.is_cancelable:
        Mollie().payments.delete(order.mollie_id)
        order.status_id = OrderStatusId.COMPLETED

    # Try to refund the order
    if order.is_refundable:
        price = order.remaining_refund_amount
        price_vat = price * order.vat_rate
        create_refund(s, mollie, order, price, price_vat)
        order.status_id = OrderStatusId.COMPLETED
