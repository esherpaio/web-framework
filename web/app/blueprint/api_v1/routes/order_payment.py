from datetime import datetime, timedelta, timezone
from enum import StrEnum

from flask import abort
from mollie.api.error import UnprocessableEntityError
from werkzeug import Response

from web.api import ApiText, json_get, json_response
from web.api.mollie import Mollie, mollie_amount, mollie_webhook
from web.app.blueprint.api_v1 import api_v1_bp
from web.auth import current_user
from web.config import config
from web.database import conn
from web.database.model import Invoice, Order
from web.i18n import _
from web.locale import current_locale

#
# Configuration
#


class Text(StrEnum):
    UNSUPPORTED_CURRENCY_BANKTRANSFER = _(
        "API_ORDER_PAYMENT_UNSUPPORTED_CURRENCY_BANKTRANSFER"
    )


#
# Endpoints
#


@api_v1_bp.post("/orders/<int:order_id>/payments")
def post_orders_id_payments(order_id: int) -> Response:
    redirect_url = json_get("redirect_url", str, nullable=False)[0]
    cancel_url = json_get("cancel_url", str, nullable=False)[0]
    methods, has_methods = json_get("methods", list)

    with conn.begin() as s:
        # Check if order is in use by the user
        order = s.query(Order).filter_by(user_id=current_user.id, id=order_id).first()
        if not order:
            return json_response(403, ApiText.HTTP_403)

        # Create Mollie payment
        order_price_vat = order.total_price * order.vat_rate
        amount = mollie_amount(order_price_vat, order.currency_code)
        description = f"Order {order.id}"
        is_test = config.MOLLIE_KEY.startswith("test")
        due_date = datetime.now(timezone.utc) + timedelta(days=25)
        due_date_str = due_date.strftime("%Y-%m-%d")
        mollie_payment_data = {
            "amount": amount,
            "description": description,
            "redirectUrl": redirect_url,
            "cancelUrl": cancel_url,
            "webhookUrl": mollie_webhook(),
            "metadata": {"order_id": order.id, "is_test": is_test},
            "dueDate": due_date_str,
            "locale": current_locale.locale_alt,
        }
        if has_methods:
            mollie_payment_data["method"] = methods
        try:
            mollie_payment = Mollie().payments.create(mollie_payment_data)
        except UnprocessableEntityError as error:
            if error.field == "amount.currency":
                abort(400, Text.UNSUPPORTED_CURRENCY_BANKTRANSFER)
            raise error

        # Create invoice
        invoice = Invoice(
            expires_at=mollie_payment.expires_at,
            paid_at=mollie_payment.paid_at,
            order_id=order.id,
            payment_url=mollie_payment.checkout_url,
        )
        s.add(invoice)
        s.flush()

        # Update order
        order.mollie_id = mollie_payment.id

    links = {"payment": mollie_payment.checkout_url}
    return json_response(links=links)


#
# Functions
#
