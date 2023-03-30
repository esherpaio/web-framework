from enum import StrEnum

from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.blueprint.api_v1.utils.order_refund import create_refund
from webshop.database.client import Conn
from webshop.database.model import Order
from webshop.database.model.user_role import UserRoleLevel
from webshop.helper.api import response, ApiText, json_get
from webshop.helper.mollie_api import Mollie
from webshop.helper.security import authorize


class _Text(StrEnum):
    VAT_NO_CONNECTION = "We are currently unable to verify your VAT number. Please try again in one hour."  # noqa: E501
    VAT_INVALID = "Your VAT number seems to be invalid. If you believe this is a mistake, please contact us."  # noqa: E501
    VAT_REQUIRED = "Your VAT number is required."
    PHONE_REQUIRED = "Your phone number is required."
    PAYMENT_INCOMPLETE = "The customer has not completed the payment yet."
    REFUND_NOT_ALLOWED = "Mollie does not allow refunds for this payment."
    REFUND_TOO_HIGH = "The requested refund price is too high."
    INVOICE_NOT_FOUND = "We cannot proceed because there is no invoice created yet."


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/orders/<int:order_id>/refunds")
def post_orders_id_refund(order_id: int) -> Response:
    price, _ = json_get("total_price", int | float, nullable=False)

    with Conn.begin() as s:
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
