from sqlalchemy.orm import Session

from web.config import config
from web.i18n import _

from .. import render_email, send_email


def mail_user_verification(
    s: Session,
    email: str,
    verification_url: str,
    **kwargs,
) -> bool:
    subject = _("MAIL_WELCOME_SUBJECT", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_WELCOME_TITLE"),
        paragraphs=[
            _("MAIL_WELCOME_P1", business_name=config.BUSINESS_NAME),
            _("MAIL_WELCOME_P2", verification_url=verification_url),
            _("MAIL_WELCOME_P3"),
        ],
    )
    return send_email(subject, html, to=[email])


def mail_user_password(
    s: Session,
    email: str,
    reset_url: str,
    **kwargs,
) -> bool:
    subject = _("MAIL_PASSWORD_SUBJECT", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_PASSWORD_TITLE"),
        paragraphs=[_("MAIL_PASSWORD_P1"), _("MAIL_PASSWORD_P2", reset_url=reset_url)],
    )
    return send_email(subject, html, to=[email])
