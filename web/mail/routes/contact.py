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
    subject = f"{config.BUSINESS_NAME} {_('MAIL_CONTACT_SUBJECT')}"
    title = _("MAIL_CONTACT_TITLE")
    paragraphs = [
        f"{_('COMMON_EMAIL')}: {email}",
        f"{_('COMMON_NAME')}: {name}",
        f"{_('COMMON_COMPANY')}: {company}",
        f"{_('COMMON_PHONE')}: {phone}",
        f"{_('COMMON_MESSAGE')}: {message}",
    ]
    html = render_email(title=title, paragraphs=paragraphs, show_unsubscribe=False)
    send_email([config.EMAIL_TO], subject, html)


def send_contact_confirmation(
    to: str,
    message: str,
) -> None:
    subject = f"{config.BUSINESS_NAME} {_('MAIL_CONTACT_SUBJECT')}"
    title = _("MAIL_CONTACT_TITLE")
    paragraphs = [
        _("MAIL_CONTACT_CONFIRMATION"),
        f"{_('COMMON_MESSAGE')}: {message}",
    ]
    html = render_email(title=title, paragraphs=paragraphs, show_unsubscribe=False)
    send_email([to], subject, html)
