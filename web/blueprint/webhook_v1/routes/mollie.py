from flask import request
from mollie.api.error import NotFoundError
from werkzeug import Response

from web.api import ApiText, json_response
from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database import conn
from web.database.model import Invoice, Order, OrderStatusId
from web.ext.mollie import Mollie
from web.mail import MailEvent, mail


@webhook_v1_bp.post("/mollie/payment")
def mollie_payment() -> Response:
    """Mollie payment webhook.

    A 200 OK response is returned if the payment is processed or when it is
    unknown to the system. The latter is recommended by Mollie for security
    reasons: https://docs.mollie.com/overview/webhooks.
    """

    mollie_payment_id = request.form.get("id")
    if not mollie_payment_id:
        return json_response()

    try:
        mollie_payment_ = Mollie().payments.get(mollie_payment_id)
    except NotFoundError:
        return json_response()

    with conn.begin() as s:
        order_id = mollie_payment_.metadata.get("order_id")
        order = s.query(Order).filter_by(id=order_id).first()
        if not order:
            return json_response(404, ApiText.HTTP_404)

        if mollie_payment_.is_paid():
            order.status_id = OrderStatusId.PAID
            s.flush()
            if not order.invoice:
                invoice = Invoice(
                    expires_at=mollie_payment_.expires_at,
                    paid_at=mollie_payment_.paid_at,
                    order_id=order.id,
                )
                s.add(invoice)
                s.flush()
                mail.trigger_events(
                    s,
                    MailEvent.ORDER_PAID,
                    order_id=order.id,
                    billing_email=order.billing.email,
                )

    return json_response()
