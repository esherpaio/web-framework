from web import config
from web.i18n.base import _
from web.mail.base import render_email, send_email


def send_order_received(
    order_id: int,
    billing_email: str,
    shipping_email: str,
    **kwargs,
) -> None:
    to = [billing_email, shipping_email]
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
    send_email(to, subject, html)


def send_order_paid(
    order_id: int,
    billing_email: str,
    invoice_number: str,
    pdf_path: str,
    **kwargs,
) -> None:
    to = [billing_email]
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    html = render_email(
        title=_("MAIL_ORDER_TITLE", order_id=order_id),
        paragraphs=[_("MAIL_ORDER_PAID_P1"), _("MAIL_ORDER_PAID_P2")],
    )
    pdf_name = _("MAIL_ORDER_PAID_FILENAME", invoice_number=invoice_number)
    send_email(to, subject, html, blob_path=pdf_path, blob_name=pdf_name)


def send_order_shipped(
    order_id: int,
    shipment_url: str,
    billing_email: str,
    shipping_email: str,
    shipping_address: str,
    **kwargs,
) -> None:
    to = [billing_email, shipping_email]
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
    send_email(to, subject, html)


def send_order_refunded(
    order_id: int,
    billing_email: str,
    refund_number: int,
    pdf_path: str,
    **kwargs,
) -> None:
    to = [billing_email]
    subject = _(
        "MAIL_ORDER_SUBJECT", business_name=config.BUSINESS_NAME, order_id=order_id
    )
    html = render_email(
        title=_("MAIL_ORDER_TITLE", order_id=order_id),
        paragraphs=[_("MAIL_ORDER_REFUNDED_P1"), _("MAIL_ORDER_REFUNDED_P2")],
    )
    pdf_name = _("MAIL_ORDER_REFUNDED_FILENAME", refund_number=refund_number)
    send_email(to, subject, html, blob_path=pdf_path, blob_name=pdf_name)
