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
    to = [config.EMAIL_TO]
    subject = _(
        "MAIL_CONTACT_SUBJECT_BUSINESS",
        business_name=config.BUSINESS_NAME,
        name=name,
    )
    html = render_email(
        title=_("MAIL_CONTACT_TITLE"),
        paragraphs=[
            _(
                "MAIL_CONTACT_DETAILS",
                name=name,
                company=company,
                email=email,
                phone=phone,
            ),
            _("MAIL_CONTACT_MESSAGE", message=message),
        ],
    )
    send_email(to, subject, html, reply_to=email)


def send_contact_customer(
    email: str,
    message: str,
    **kwargs,
) -> None:
    to = [email]
    subject = _("MAIL_CONTACT_SUBJECT_CUSTOMER", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_CONTACT_TITLE"),
        paragraphs=[
            _("MAIL_CONTACT_CONFIRMATION"),
            _("MAIL_CONTACT_MESSAGE", message=message),
        ],
    )
    send_email(to, subject, html)
