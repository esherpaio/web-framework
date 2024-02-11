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
from web.ext.mollie import Mollie
from web.i18n.base import _
from web.libs.api import ApiText, response
from web.libs.auth import access_control
from web.libs.cart import get_shipment_methods
from web.mail.base import MailEvent, mail

#
# Configuration
#


class Text(StrEnum):
    PHONE_REQUIRED = _("API_ORDER_PHONE_REQUIRED")
    STATE_REQUIRED = _("API_ORDER_STATE_REQUIRED")
    STATUS_INVALID = _("API_ORDER_STATUS_INVALID")
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
    patch_columns = {
        Order.status_id,
    }


#
# Endpoints
#


@api_v1_bp.post("/orders")
def post_orders() -> Response:
    api = OrderAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = api.model()
        get_cart(s, data, model)
        val_cart(s, data, model)
        set_order(s, data, model)
        api.insert(s, data, model)
        set_order_lines(s, data, model)
        mail_order(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.patch("/orders/<int:order_id>")
@access_control(UserRoleLevel.ADMIN)
def patch_orders_id(order_id: int) -> Response:
    api = OrderAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        model: Order = api.get(s, order_id)
        val_status(s, data, model)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.delete("/orders/<int:order_id>")
@access_control(UserRoleLevel.ADMIN)
def delete_orders_id(order_id: int) -> Response:
    api = OrderAPI()
    data = api.gen_view_args_data()
    with conn.begin() as s:
        model: Order = api.get(s, order_id)
        cancel_mollie(s, data, model)
    return response()


#
# Functions
#


def get_cart(s: Session, data: dict, model: Order) -> None:
    cart_id = data["cart_id"]
    filters = {Cart.id == cart_id, Cart.user_id == current_user.id}
    cart = s.query(Cart).filter(*filters).first()
    if cart is None:
        abort(response(404, ApiText.HTTP_404))
    g.cart = cart


def val_status(s: Session, data: dict, model: Order) -> None:
    if data["status_id"] not in model.next_statuses:
        abort(response(400, Text.STATUS_INVALID))


def val_cart(s: Session, data: dict, model: Order) -> None:
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
    # Check state
    if cart.billing.country.state_required:
        if cart.billing.state is None:
            abort(response(400, Text.STATE_REQUIRED))


def set_order(s: Session, data: dict, model: Order) -> None:
    cart = g.cart
    if cart.coupon is not None:
        model.coupon_amount = cart.coupon.amount
        model.coupon_code = cart.coupon.code
        model.coupon_rate = cart.coupon.rate
    if cart.shipment_method is not None:
        model.shipment_name = cart.shipment_method.name
    model.billing_id = cart.billing_id
    model.currency_id = cart.currency_id
    model.shipment_price = cart.shipment_price
    model.shipping_id = cart.shipping_id
    model.total_price = cart.total_price
    model.vat_rate = cart.vat_rate
    model.vat_reverse = cart.vat_reverse
    model.user_id = current_user.id
    model.status_id = OrderStatusId.PENDING


def set_order_lines(s: Session, data: dict, model: Order) -> None:
    cart = g.cart
    order_lines = []
    for cart_item in cart.items:
        order_line = OrderLine()
        order_line.order_id = model.id
        order_line.sku_id = cart_item.sku_id
        order_line.quantity = cart_item.quantity
        order_line.total_price = cart_item.total_price
        order_lines.append(order_line)
    s.add_all(order_lines)
    s.flush()
    g.order_lines = order_lines


def mail_order(s: Session, data: dict, model: Order) -> None:
    for event in mail.get_events(MailEvent.ORDER_RECEIVED):
        event(
            order_id=model.id,
            billing_email=model.billing.email,
            shipping_email=model.shipping.email,
        )


def cancel_mollie(s: Session, data: dict, model: Order) -> None:
    # Try to cancel the Mollie payment
    mollie = Mollie().payments.get(model.mollie_id)
    if mollie.is_cancelable:
        Mollie().payments.delete(model.mollie_id)
        model.status_id = OrderStatusId.COMPLETED

    # Try to refund the order
    if model.is_refundable:
        price = model.remaining_refund_amount
        price_vat = price * model.vat_rate
        create_refund(s, mollie, model, price, price_vat)
        model.status_id = OrderStatusId.COMPLETED
