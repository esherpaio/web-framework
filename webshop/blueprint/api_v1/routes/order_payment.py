from datetime import datetime, timedelta

from flask import Response, url_for
from flask_login import current_user

from webshop import config
from webshop.blueprint.api_v1 import api_v1_bp
from webshop.database.client import Conn
from webshop.database.model import Order
from webshop.helper.api import response, ApiText
from webshop.helper.mollie_api import Mollie, mollie_amount, mollie_webhook
from webshop.helper.security import get_access


@api_v1_bp.post("/orders/<int:order_id>/payments")
def post_orders_id_payments(order_id: int) -> Response:
    with Conn.begin() as s:
        # Authorize request
        # Get order
        # Raise if order doesn't exist
        access = get_access(s)
        order = s.query(Order).filter_by(access_id=access.id, id=order_id).first()
        if not order:
            return response(403, ApiText.HTTP_403)

        # Create Mollie payment
        amount = mollie_amount(order.total_price * order.vat_rate, order.currency.code)
        description = f"Order {order.id}"
        redirect = url_for(
            "checkout.confirmation",
            _locale=current_user.locale,
            order_id=order.id,
            _external=True,
        )
        due_date = (datetime.utcnow() + timedelta(days=100)).strftime("%Y-%m-%d")
        mollie_payment = Mollie().payments.create(
            {
                "amount": amount,
                "description": description,
                "redirectUrl": redirect,
                "webhookUrl": mollie_webhook(),
                "metadata": {"order_id": order.id, "is_test": config.MOLLIE_TEST},
                "dueDate": due_date,
            }
        )

        # Update order
        order.mollie_id = mollie_payment.id

    links = {"payment": mollie_payment.checkout_url}
    return response(links=links)
