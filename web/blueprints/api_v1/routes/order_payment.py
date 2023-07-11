from datetime import datetime, timedelta

from flask import Response, url_for
from flask_login import current_user

from web import config
from web.blueprints.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Order
from web.helper.api import ApiText, response
from web.helper.mollie_api import Mollie, mollie_amount, mollie_webhook


@api_v1_bp.post("/orders/<int:order_id>/payments")
def post_orders_id_payments(order_id: int) -> Response:
    with conn.begin() as s:
        # Check if order is in use by the user
        order = s.query(Order).filter_by(user_id=current_user.id, id=order_id).first()
        if not order:
            return response(403, ApiText.HTTP_403)

        # Create Mollie payment
        order_price_vat = order.total_price * order.vat_rate
        amount = mollie_amount(order_price_vat, order.currency.code)
        description = f"Order {order.id}"
        redirect = url_for("checkout.confirmation", order_id=order.id, _external=True)
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
    return response(links=links)
