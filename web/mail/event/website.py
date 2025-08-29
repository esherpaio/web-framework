from sqlalchemy.orm import Session

from web.i18n import _
from web.setup import config

from .. import render_email, send_email


def mail_contact_business(
    s: Session,
    email: str,
    name: str,
    message: str,
    company: str | None = None,
    phone: str | None = None,
    **kwargs,
) -> bool:
    subject = _(
        "MAIL_CONTACT_SUBJECT_BUSINESS", business_name=config.BUSINESS_NAME, name=name
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
    return send_email(subject, html, to=[config.MAIL_RECEIVER], reply_to=email)


def mail_contact_customer(
    s: Session,
    email: str,
    message: str,
    **kwargs,
) -> bool:
    subject = _("MAIL_CONTACT_SUBJECT_CUSTOMER", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_CONTACT_TITLE"),
        paragraphs=[
            _("MAIL_CONTACT_CONFIRMATION"),
            _("MAIL_CONTACT_MESSAGE", message=message),
        ],
    )
    return send_email(subject, html, to=[email])


def mail_bulk(
    s: Session,
    emails: list[str],
    subject: str,
    html: str,
    **kwargs,
) -> bool:
    html = render_email("html", title=subject, html=html)
    return send_email(subject, html, bcc=emails)
