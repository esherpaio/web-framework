from web import config
from web.i18n.base import _
from web.mail.base import render_email, send_email
from web.mail.utils import pdf_to_string


def send_order_received(
    order_id: int,
    billing_email: str,
    shipping_email: str,
) -> None:
    to = [billing_email, shipping_email]
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    title = _("MAIL_ORDER_TITLE", order_id=order_id)
    paragraphs = [
        _("MAIL_ORDER_RECEIVED_P1", business_name=config.BUSINESS_NAME),
        _("MAIL_ORDER_RECEIVED_P2"),
    ]
    html = render_email(title, paragraphs)
    send_email(to, subject, html)


def send_order_paid(
    order_id: int,
    billing_email: str,
    invoice_id: int,
    pdf_path: str,
) -> None:
    to = [billing_email]
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    title = _("MAIL_ORDER_TITLE", order_id=order_id)
    paragraphs = [_("MAIL_ORDER_PAID_P1"), _("MAIL_ORDER_PAID_P2")]
    pdf_name = _("MAIL_ORDER_PAID_FILENAME", invoice_id=str(invoice_id))
    html = render_email(title, paragraphs)
    send_email(to, subject, html, pdf_path, pdf_name)


def send_order_shipped(
    order_id: int,
    shipment_url: str,
    billing_email: str,
    shipping_email: str,
    shipping_address: str,
) -> None:
    to = [billing_email, shipping_email]
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    title = _("MAIL_ORDER_TITLE", order_id=order_id)
    paragraphs = [
        _("MAIL_ORDER_SHIPPED_P1"),
        _("MAIL_ORDER_SHIPPED_P2", shipment_url=shipment_url),
        _("MAIL_ORDER_SHIPPED_P3", shipping_address=shipping_address),
    ]
    html = render_email(title, paragraphs)
    send_email(to, subject, html)


def send_order_refunded(
    order_id: int,
    billing_email: str,
    refund_id: int,
    pdf_path: str,
) -> None:
    to = [billing_email]
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    title = _("MAIL_ORDER_TITLE", order_id=order_id)
    paragraphs = [_("MAIL_ORDER_REFUNDED_P1"), _("MAIL_ORDER_REFUNDED_P2")]
    pdf_name = _("MAIL_ORDER_REFUNDED_FILENAME", refund_id=refund_id)
    html = render_email(title, paragraphs)
    send_email(to, subject, html, pdf_path, pdf_name)
