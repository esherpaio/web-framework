import typing

from flask import abort
from flask_login import current_user
from mollie.api.objects.payment import Payment
from sqlalchemy.orm import Session

from web.database.model import Cart, Order, Refund
from web.document.objects.refund import gen_refund
from web.helper.api import ApiText, response
from web.helper.builtins import none_aware_attrgetter
from web.helper.cart import get_shipment_methods
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
    _, pdf_path = gen_refund(s, order, order.invoice, refund)
    send_order_refunded(
        order_id=order.id,
        billing_email=order.billing.email,
        refund_number=refund.number,
        pdf_path=pdf_path,
    )
    remove_file(pdf_path)


def authorize_cart(s: Session, data: dict) -> Cart | typing.NoReturn:
    cart_id = data["cart_id"]
    filters = {Cart.id == cart_id, Cart.user_id == current_user.id}
    cart = s.query(Cart).filter(*filters).first()
    if cart is None:
        abort(response(404, ApiText.HTTP_404))
    else:
        return cart


def update_cart_shipment_methods(s: Session, cart: Cart) -> None:
    shipment_methods = get_shipment_methods(s, cart)
    if shipment_methods:
        shipment_method = min(shipment_methods, key=none_aware_attrgetter("unit_price"))
        cart.shipment_method_id = shipment_method.id
        cart.shipment_price = shipment_method.unit_price * cart.currency.rate
    else:
        cart.shipment_method_id = None
        cart.shipment_price = 0
    s.flush()
