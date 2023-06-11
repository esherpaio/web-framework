from web import config
from web.i18n.base import _
from web.mail.base import render_email, send_email


def send_contact(
    email: str,
    name: str,
    message: str,
    company: str | None = None,
    phone: str | None = None,
) -> None:
    subject = _("MAIL_CONTACT_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_CONTACT_TITLE")
    paragraphs = [
        _("MAIL_CONTACT_DETAILS", name=name, company=company, email=email, phone=phone),
        _("MAIL_CONTACT_MESSAGE", message=message),
    ]
    html = render_email(title, paragraphs)
    send_email([config.EMAIL_TO], subject, html)


def send_contact_confirmation(
    to: str,
    message: str,
) -> None:
    subject = _("MAIL_CONTACT_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_CONTACT_TITLE")
    paragraphs = [
        _("MAIL_CONTACT_CONFIRMATION"),
        _("MAIL_CONTACT_MESSAGE", message=message),
    ]
    html = render_email(title, paragraphs)
    send_email([to], subject, html)
