from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Invoice, Order, Refund
from web.document.object import gen_invoice, gen_refund
from web.i18n import _
from web.utils import remove_file

from ..base import render_email, send_email


def mail_order_received(
    s: Session,
    order_id: int,
    billing_email: str,
    shipping_email: str,
    **kwargs,
) -> bool:
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    html = render_email(
        title=_("MAIL_ORDER_TITLE", order_id=order_id),
        paragraphs=[
            _("MAIL_ORDER_RECEIVED_P1", business_name=config.BUSINESS_NAME),
            _("MAIL_ORDER_RECEIVED_P2"),
        ],
    )
    return send_email(subject, html, to=[billing_email, shipping_email])


def mail_order_paid(
    s: Session,
    order_id: int,
    billing_email: str,
    **kwargs,
) -> bool:
    # Generate invoice
    order = s.query(Order).filter_by(id=order_id).one()
    invoice = s.query(Invoice).filter_by(order_id=order_id).one()
    pdf_name, pdf_path = gen_invoice(s, order, invoice)
    remove_file(pdf_path, delay_s=20)
    # Generate and send email
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    html = render_email(
        title=_("MAIL_ORDER_TITLE", order_id=order_id),
        paragraphs=[_("MAIL_ORDER_PAID_P1"), _("MAIL_ORDER_PAID_P2")],
    )
    return send_email(
        subject, html, to=[billing_email], blob_path=pdf_path, blob_name=pdf_name
    )


def mail_order_shipped(
    s: Session,
    order_id: int,
    shipment_url: str,
    billing_email: str,
    shipping_email: str,
    shipping_address: str,
    **kwargs,
) -> bool:
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    html = render_email(
        title=_("MAIL_ORDER_TITLE", order_id=order_id),
        paragraphs=[
            _("MAIL_ORDER_SHIPPED_P1"),
            _("MAIL_ORDER_SHIPPED_P2", shipment_url=shipment_url),
            _("MAIL_ORDER_SHIPPED_P3", shipping_address=shipping_address),
        ],
    )
    return send_email(subject, html, to=[billing_email, shipping_email])


def mail_order_refunded(
    s: Session,
    order_id: int,
    refund_id: int,
    billing_email: str,
    **kwargs,
) -> bool:
    # Generate refund
    order = s.query(Order).filter_by(id=order_id).one()
    invoice = s.query(Invoice).filter_by(order_id=order_id).one()
    refund = s.query(Refund).filter_by(id=refund_id).one()
    pdf_name, pdf_path = gen_refund(s, order, invoice, refund)
    remove_file(pdf_path, delay_s=20)
    # Generate and send email
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    html = render_email(
        title=_("MAIL_ORDER_TITLE", order_id=order_id),
        paragraphs=[_("MAIL_ORDER_REFUNDED_P1"), _("MAIL_ORDER_REFUNDED_P2")],
    )
    return send_email(
        subject, html, to=[billing_email], blob_path=pdf_path, blob_name=pdf_name
    )
