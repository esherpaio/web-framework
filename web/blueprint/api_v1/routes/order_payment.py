from datetime import datetime, timedelta

from werkzeug import Response

from web.api.utils import ApiText, json_get, json_response
from web.auth import current_user
from web.blueprint.api_v1 import api_v1_bp
from web.config import config
from web.database import conn
from web.database.model import Order
from web.ext.mollie import Mollie, mollie_amount, mollie_webhook

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/orders/<int:order_id>/payments")
def post_orders_id_payments(order_id: int) -> Response:
    redirect = json_get("redirect", str, nullable=False)

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
        due_date = (datetime.utcnow() + timedelta(days=100)).strftime("%Y-%m-%d")
        mollie_payment = Mollie().payments.create(
            {
                "amount": amount,
                "description": description,
                "redirectUrl": redirect,
                "webhookUrl": mollie_webhook(),
                "metadata": {"order_id": order.id, "is_test": is_test},
                "dueDate": due_date,
            }
        )

        # Update order
        order.mollie_id = mollie_payment.id

    links = {"payment": mollie_payment.checkout_url}
    return json_response(links=links)


#
# Functions
#
