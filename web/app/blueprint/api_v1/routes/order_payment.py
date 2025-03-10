from enum import StrEnum

from mollie.api.error import UnprocessableEntityError
from werkzeug import Response

from web.api import json_get
from web.api.mollie import Mollie, gen_mollie_payment_data
from web.api.response import HttpText, json_response
from web.app.blueprint.api_v1 import api_v1_bp
from web.auth import current_user
from web.database import conn
from web.database.model import Invoice, Order
from web.i18n import _

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
    methods = json_get("methods", list)[0]

    with conn.begin() as s:
        # Check if order is in use by the user
        order = s.query(Order).filter_by(user_id=current_user.id, id=order_id).first()
        if not order:
            return json_response(403, HttpText.HTTP_403)

        # Create Mollie payment
        mollie_payment_data = gen_mollie_payment_data(
            s,
            order,
            redirect_url,
            cancel_url,
            methods,
        )
        try:
            mollie_payment = Mollie().payments.create(mollie_payment_data)
        except UnprocessableEntityError as error:
            if error.field == "amount.currency":
                return json_response(400, Text.UNSUPPORTED_CURRENCY_BANKTRANSFER)
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
