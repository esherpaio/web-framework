from enum import StrEnum

from flask import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.utils.order_refund import create_refund
from web.database.client import conn
from web.database.model import Order, UserRoleLevel
from web.helper.api import ApiText, authorize, json_get, response
from web.helper.mollie_api import Mollie
from web.i18n.base import _


class _Text(StrEnum):
    PAYMENT_INCOMPLETE = _("API_ORDER_REFUND_PAYMENT_INCOMPLETE")
    REFUND_NOT_ALLOWED = _("API_ORDER_REFUND_NOT_ALLOWED")
    REFUND_TOO_HIGH = _("API_ORDER_REFUND_TOO_HIGH")
    INVOICE_NOT_FOUND = _("API_ORDER_REFUND_INVOICE_NOT_FOUND")


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/orders/<int:order_id>/refunds")
def post_orders_id_refund(order_id: int) -> Response:
    price, _ = json_get("total_price", int | float, nullable=False)

    with conn.begin() as s:
        # Get order
        # Raise if order doesn't exist
        order = s.query(Order).filter_by(id=order_id).first()
        if not order:
            return response(404, ApiText.HTTP_404)

        # Raise if invoice doesn't exist
        if not order.invoice:
            return response(400, _Text.INVOICE_NOT_FOUND)

        # Raise if mollie_id doesn't exist
        if not order.mollie_id:
            return response(404, _Text.PAYMENT_INCOMPLETE)

        # Check if Mollie allows a refund
        mollie_payment = Mollie().payments.get(order.mollie_id)
        if not mollie_payment.can_be_refunded:
            return response(404, _Text.REFUND_NOT_ALLOWED)

        # Check if refund price is OK
        price_vat = round(price * order.vat_rate, 2)
        if price > order.remaining_refund_amount:
            return response(400, _Text.REFUND_TOO_HIGH)

        # Create refund
        create_refund(s, mollie_payment, order, price, price_vat)

    return response()
