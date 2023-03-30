from mollie.api.objects.payment import Payment
from sqlalchemy.orm import Session

from webshop.database.model import Order, Refund
from webshop.document.objects.refund import gen_refund
from webshop.helper.fso import remove_file
from webshop.helper.mollie_api import Mollie, mollie_amount
from webshop.mail.routes.order import send_order_refund


def create_refund(
    s: Session,
    mollie_payment: Payment,
    order: Order,
    price: float,
    price_vat: float,
) -> None:
    # Insert refund
    refund_price = abs(price) * -1
    refund = Refund(order_id=order.id, total_price=refund_price)
    s.add(refund)
    s.flush()

    # Create Mollie refund
    mollie_refund = (
        Mollie()
        .payment_refunds.on(mollie_payment)
        .create({"amount": mollie_amount(price_vat, order.currency.code)})
    )

    # Update refund
    refund.mollie_id = mollie_refund.id
    s.flush()

    # Send email
    _, pdf_path = gen_refund(order, order.invoice, refund)
    send_order_refund(order.id, order.billing.email, refund.id, pdf_path)
    remove_file(pdf_path)
