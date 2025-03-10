from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Invoice, Order, Refund
from web.document import get_pdf_path
from web.document.object import gen_invoice_pdf, gen_refund_pdf
from web.i18n import _
from web.utils import remove_file

from .. import render_email, send_email


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
    pdf = gen_invoice_pdf(s, order, invoice)
    pdf_name = _("PDF_INVOICE_FILENAME", invoice_number=invoice.number)
    pdf_path = get_pdf_path(pdf_name)
    pdf.output(pdf_path)
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
    pdf = gen_refund_pdf(s, order, invoice, refund)
    pdf_name = _("PDF_REFUND_FILENAME", refund_number=refund.number)
    pdf_path = get_pdf_path(pdf_name)
    pdf.output(pdf_path)
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
