from enum import StrEnum

from werkzeug import Response

from web.api import ApiText, json_get, json_response
from web.app.blueprint import api_v1_bp
from web.auth import authorize
from web.database import conn
from web.database.model import Order, UserRoleLevel
from web.ext.mollie import Mollie
from web.i18n import _

from ._common import create_refund

#
# Configuration
#


class Text(StrEnum):
    INVOICE_NOT_FOUND = _("API_ORDER_REFUND_INVOICE_NOT_FOUND")
    PAYMENT_INCOMPLETE = _("API_ORDER_REFUND_PAYMENT_INCOMPLETE")
    REFUND_NOT_ALLOWED = _("API_ORDER_REFUND_NOT_ALLOWED")
    REFUND_TOO_HIGH = _("API_ORDER_REFUND_TOO_HIGH")


#
# Endpoints
#


@api_v1_bp.post("/orders/<int:order_id>/refunds")
@authorize(UserRoleLevel.ADMIN)
def post_orders_id_refund(order_id: int) -> Response:
    price, _ = json_get("total_price", int | float, nullable=False)

    with conn.begin() as s:
        # Get order
        order = s.query(Order).filter_by(id=order_id).first()
        if not order:
            return json_response(404, ApiText.HTTP_404)

        # Check if an invoice exists
        if not order.invoice:
            return json_response(400, Text.INVOICE_NOT_FOUND)

        # Check if the order has a Mollie ID
        if not order.mollie_id:
            return json_response(404, Text.PAYMENT_INCOMPLETE)

        # Check if Mollie allows a refund
        mollie_payment = Mollie().payments.get(order.mollie_id)
        if not mollie_payment.can_be_refunded():
            return json_response(404, Text.REFUND_NOT_ALLOWED)

        # Generate price
        if price > order.remaining_refund_amount:
            price = order.remaining_refund_amount
        price_vat = round(price * order.vat_rate, 2)

        # Create refund
        create_refund(s, mollie_payment, order, price, price_vat)

    return json_response()


#
# Functions
#
