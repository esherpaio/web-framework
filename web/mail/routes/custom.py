from web import config
from web.i18n.base import _
from web.mail.base import render_email, send_email

# Mertens Keukenambacht


def send_custom_1(
    name: str,
    email: str,
    message: str,
    phone: str | None = None,
    found_by: str | None = None,
) -> None:
    to = [config.EMAIL_TO]
    subject = _("MAIL_CUSTOM_1_SUBJECT", business_name=config.BUSINESS_NAME)
    title = _("MAIL_CUSTOM_1_TITLE")
    paragraphs = [
        _(
            "MAIL_CUSTOM_1_P1",
            name=name,
            email=email,
            phone=phone,
            found_by=found_by,
        ),
        _(
            "MAIL_CUSTOM_1_MESSAGE",
            message=message,
        ),
    ]
    html = render_email(title, paragraphs)
    send_email(to, subject, html)
