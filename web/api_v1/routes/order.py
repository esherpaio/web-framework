from enum import StrEnum

from flask import Response
from flask_login import current_user
from pyvat import check_vat_number

from web.api_v1 import api_v1_bp
from web.api_v1.common.order_refund import create_refund
from web.api_v1.resource.order import get_resource
from web.database.client import conn
from web.database.model import Cart, Order, OrderLine, OrderStatusId, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.cart import get_shipment_methods
from web.helper.mollie_api import Mollie
from web.helper.user import access_control
from web.i18n.base import _
from web.mail.routes.order import send_order_received


class _Text(StrEnum):
    VAT_NO_CONNECTION = _("API_ORDER_VAT_NO_CONNECTION")
    VAT_INVALID = _("API_ORDER_VAT_INVALID")
    VAT_REQUIRED = _("API_ORDER_VAT_REQUIRED")
    PHONE_REQUIRED = _("API_ORDER_PHONE_REQUIRED")


@api_v1_bp.post("/orders")
def post_orders() -> Response:
    cart_id, has_cart_id = json_get("cart_id", int)

    with conn.begin() as s:
        # Authorize request
        # Get cart
        # Raise if cart doesn't exist
        cart = s.query(Cart).filter_by(user_id=current_user.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Check shipping_id
        if cart.shipping_id is None:
            return response(400, ApiText.HTTP_400)

        # Check billing_id
        if cart.billing_id is None:
            return response(400, ApiText.HTTP_400)

        # Check if shipment_method_id is set
        shipment_methods = get_shipment_methods(s, cart)
        if shipment_methods and not cart.shipment_method_id:
            return response(400, ApiText.HTTP_400)

        # Check if shipment_method_id is valid
        shipment_method_ids = [x.id for x in shipment_methods]
        if cart.shipment_method_id:
            if cart.shipment_method_id not in shipment_method_ids:
                return response(400, ApiText.HTTP_400)

        # Check phone for shipping_method
        if cart.shipment_method:
            if cart.shipment_method.phone_required and not cart.billing.phone:
                return response(400, _Text.PHONE_REQUIRED)

        # Check VAT required in Europe
        if (
            cart.billing.company
            and cart.billing.country.region.is_europe
            and not cart.billing.vat
        ):
            return response(400, _Text.VAT_REQUIRED)

        # Check VAT with pyvat
        if cart.billing.vat:
            vat_parsed = "".join(x for x in cart.billing.vat if x.isalnum())
            vat_result = check_vat_number(
                vat_parsed, country_code=cart.billing.country.code
            )
            if vat_result.is_valid is None:
                return response(500, _Text.VAT_NO_CONNECTION)
            if not vat_result.is_valid:
                return response(400, _Text.VAT_INVALID)

        # Insert order
        order = Order(
            access_id=access.id,
            billing_id=cart.billing_id,
            coupon_amount=cart.coupon.amount if cart.coupon else None,
            coupon_code=cart.coupon.code if cart.coupon else None,
            coupon_rate=cart.coupon.rate if cart.coupon else None,
            currency_id=cart.currency_id,
            shipment_name=cart.shipment_method.name if cart.shipment_method else None,
            shipment_price=cart.shipment_price,
            shipping_id=cart.shipping_id,
            status_id=OrderStatusId.PENDING,
            total_price=cart.total_price,
            vat_rate=cart.vat_rate,
            vat_reverse=cart.vat_reverse,
        )
        s.add(order)
        s.flush()

        # Insert order lines
        for cart_item in cart.items:
            order_line = OrderLine(
                order_id=order.id,
                quantity=cart_item.quantity,
                sku_id=cart_item.sku_id,
                total_price=cart_item.total_price,
            )
            s.add(order_line)
            s.flush()

        # Send email
        send_order_received(
            order_id=order.id,
            billing_email=order.billing.email,
            shipping_email=order.shipping.email,
        )

    resource = get_resource(order.id)
    return response(data=resource)


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/orders/<int:order_id>")
def delete_orders_id(order_id: int) -> Response:
    with conn.begin() as s:
        # Get order
        # Raise if order doesn't exist
        order = s.query(Order).filter_by(id=order_id).first()
        if not order:
            return response(404, ApiText.HTTP_404)

        # Try to cancel the Mollie payment
        # Update order status
        mollie_payment = Mollie().payments.get(order.mollie_id)
        if mollie_payment.is_cancelable:
            Mollie().payments.delete(order.mollie_id)
            order.status_id = OrderStatusId.COMPLETED

        # Check if order is refundable
        # Create refund
        # Update order
        if order.is_refundable:
            price = order.remaining_refund_amount
            price_vat = price * order.vat_rate
            create_refund(s, mollie_payment, order, price, price_vat)
            order.status_id = OrderStatusId.COMPLETED

    return response()
