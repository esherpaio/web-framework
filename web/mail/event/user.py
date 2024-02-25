from web.config import config
from web.i18n.base import _
from web.mail.utils import render_email, send_email


def mail_user_verification(
    email: str,
    verification_url: str,
    **kwargs,
) -> None:
    to = [email]
    subject = _("MAIL_WELCOME_SUBJECT", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_WELCOME_TITLE"),
        paragraphs=[
            _("MAIL_WELCOME_P1", business_name=config.BUSINESS_NAME),
            _("MAIL_WELCOME_P2", verification_url=verification_url),
            _("MAIL_WELCOME_P3"),
        ],
    )
    send_email(to, subject, html)


def mail_user_password(
    email: str,
    reset_url: str,
    **kwargs,
) -> None:
    to = [email]
    subject = _("MAIL_PASSWORD_SUBJECT", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_PASSWORD_TITLE"),
        paragraphs=[_("MAIL_PASSWORD_P1"), _("MAIL_PASSWORD_P2", reset_url=reset_url)],
    )
    send_email(to, subject, html)
