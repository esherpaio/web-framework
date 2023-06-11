from web import config
from web.i18n.base import _
from web.mail.base import render_email, send_email


def send_verification_url(
    to: str,
    verification_url: str,
) -> None:
    subject = _("MAIL_WELCOME_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_WELCOME_TITLE")
    paragraphs = [
        _("MAIL_WELCOME_P1", business_name=config.BUSINESS_NAME),
        _("MAIL_WELCOME_P2", verification_url=verification_url),
        _("MAIL_WELCOME_P3"),
    ]
    html = render_email(title, paragraphs)
    send_email([to], subject, html)


def send_new_password(
    to: str,
    reset_url: str,
) -> None:
    subject = _("MAIL_PASSWORD_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_PASSWORD_TITLE")
    paragraphs = [_("MAIL_PASSWORD_P1"), _("MAIL_PASSWORD_P2", reset_url=reset_url)]
    html = render_email(title, paragraphs)
    send_email([to], subject, html)
