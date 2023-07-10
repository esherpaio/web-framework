from mollie.api.objects.payment import Payment
from sqlalchemy.orm import Session

from web.database.model import Order, Refund
from web.document.objects.refund import gen_refund
from web.helper.fso import remove_file
from web.helper.mollie_api import Mollie, mollie_amount
from web.mail.routes.order import send_order_refunded


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
    mollie_payment = Mollie().payments.get(order.mollie_id)
    mollie_refund = mollie_payment.refunds.create(
        {"amount": mollie_amount(price_vat, order.currency.code)}
    )

    # Update refund
    refund.mollie_id = mollie_refund.id
    s.flush()

    # Send email
    _, pdf_path = gen_refund(order, order.invoice, refund)
    send_order_refunded(
        order_id=order.id,
        billing_email=order.billing.email,
        refund_number=refund.number,
        pdf_path=pdf_path,
    )
    remove_file(pdf_path)
