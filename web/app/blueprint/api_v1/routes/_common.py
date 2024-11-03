import uuid

from mollie.api.objects.payment import Payment
from sqlalchemy.orm import Session

from web.app.urls import parse_url, url_for
from web.config import config
from web.database.model import Order, Refund, User, Verification
from web.app.ext.mollie import Mollie, mollie_amount
from web.mail import MailEvent, mail


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
        {"amount": mollie_amount(price_vat, order.currency_code)}
    )

    # Update refund
    refund.mollie_id = mollie_refund.id
    s.flush()

    # Send email
    mail.trigger_events(
        s,
        MailEvent.ORDER_REFUNDED,
        order_id=order.id,
        refund_id=refund.id,
        billing_email=order.billing.email,
    )


def recover_user_password(s: Session, user: User) -> None:
    # Insert verification
    key = str(uuid.uuid4())
    verification = Verification(user_id=user.id, key=key)
    s.add(verification)
    s.flush()

    # Send email
    reset_url = parse_url(
        config.ENDPOINT_PASSWORD,
        _func=url_for,
        _external=True,
        verification_key=verification.key,
    )
    mail.trigger_events(
        s,
        MailEvent.USER_REQUEST_PASSWORD,
        email=user.email,
        reset_url=reset_url,
    )
