from datetime import datetime, timedelta, timezone
from enum import StrEnum

from mollie.api.error import UnprocessableEntityError
from werkzeug import Response

from web.api import ApiText, json_get, json_response
from web.api.mollie import (
    DEFAULT_LOCALE,
    VALID_LOCALES,
    Mollie,
    mollie_amount,
    mollie_webhook,
)
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

        # Generate Mollie data
        order_price_vat = order.total_price * order.vat_rate
        m_amount = mollie_amount(order_price_vat, order.currency_code)
        m_description = f"Order {order.id}"
        m_is_test = config.MOLLIE_KEY.startswith("test")
        due_date = datetime.now(timezone.utc) + timedelta(days=25)
        m_due_date = due_date.strftime("%Y-%m-%d")
        m_locale = current_locale.locale_alt
        if current_locale.locale_alt not in VALID_LOCALES:
            m_locale = DEFAULT_LOCALE
        m_data = {
            "amount": m_amount,
            "description": m_description,
            "redirectUrl": redirect_url,
            "cancelUrl": cancel_url,
            "webhookUrl": mollie_webhook(),
            "metadata": {"order_id": order.id, "is_test": m_is_test},
            "dueDate": m_due_date,
            "locale": m_locale,
        }
        if has_methods:
            m_data["method"] = methods

        # Create Mollie payment
        try:
            m_payment = Mollie().payments.create(m_data)
        except UnprocessableEntityError as error:
            if error.field == "amount.currency":
                return json_response(400, Text.UNSUPPORTED_CURRENCY_BANKTRANSFER)
            raise error

        # Create invoice
        invoice = Invoice(
            expires_at=m_payment.expires_at,
            paid_at=m_payment.paid_at,
            order_id=order.id,
            payment_url=m_payment.checkout_url,
        )
        s.add(invoice)
        s.flush()

        # Update order
        order.mollie_id = m_payment.id

    links = {"payment": m_payment.checkout_url}
    return json_response(links=links)


#
# Functions
#
