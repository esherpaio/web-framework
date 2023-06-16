from web import config
from web.i18n.base import _
from web.mail.base import render_email, send_email


def send_contact_business(
    email: str,
    name: str,
    message: str,
    company: str | None = None,
    phone: str | None = None,
    **kwargs,
) -> None:
    subject = _("MAIL_CONTACT_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_CONTACT_TITLE")
    paragraphs = [
        _("MAIL_CONTACT_DETAILS", name=name, company=company, email=email, phone=phone),
        _("MAIL_CONTACT_MESSAGE", message=message),
    ]
    html = render_email(title, paragraphs)
    send_email([config.BUSINESS_EMAIL], subject, html)


def send_contact_customer(
    email: str,
    message: str,
    **kwargs,
) -> None:
    subject = _("MAIL_CONTACT_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_CONTACT_TITLE")
    paragraphs = [
        _("MAIL_CONTACT_CONFIRMATION"),
        _("MAIL_CONTACT_MESSAGE", message=message),
    ]
    html = render_email(title, paragraphs)
    send_email([email], subject, html)


if __name__ == "__main__":
    send_contact_business(
        email="contact@enlarge-online.nl",
        name="John Doe",
        message="Hello world",
        company="Enlarge Online",
        phone="+31612345678",
    )
