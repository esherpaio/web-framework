from flask import Response, request
from mollie.api.error import NotFoundError

from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import Invoice, Order
from web.database.model.order_status import OrderStatusId
from web.document.objects.invoice import gen_invoice
from web.helper.api import ApiText, response
from web.helper.fso import remove_file
from web.helper.mollie_api import Mollie
from web.mail.routes.order import send_order_paid


@webhook_v1_bp.post("/mollie/payment")
def mollie_payment() -> Response:
    """Mollie payment webhook.

    A 200 OK response is returned if the payment is processed or when it is unknown to
    our system. The latter is recommended by Mollie for security reasons:
    https://docs.mollie.com/overview/webhooks.
    """

    mollie_payment_id = request.form.get("id")
    if not mollie_payment_id:
        return response()

    try:
        mollie_payment_ = Mollie().payments.get(mollie_payment_id)
    except NotFoundError:
        return response()

    with conn.begin() as s:
        order_id = mollie_payment_.metadata.get("order_id")
        order = s.query(Order).filter_by(id=order_id).first()
        if not order:
            return response(404, ApiText.HTTP_404)

        if mollie_payment_.is_paid() and not order.invoice:
            invoice = Invoice(
                expires_at=mollie_payment_.expires_at,
                paid_at=mollie_payment_.paid_at,
                order_id=order.id,
            )
            s.add(invoice)
            order.status_id = OrderStatusId.PAID
            s.flush()
            _, pdf_path = gen_invoice(order, invoice)
            send_order_paid(
                order_id=order.id,
                billing_email=order.billing.email,
                invoice_number=invoice.number,
                pdf_path=pdf_path,
            )
            remove_file(pdf_path)

    return response()
