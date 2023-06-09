from web import config
from web.mail.base import render_email, send_email


def send_verification_url(
    to: str,
    verification_url: str,
) -> None:
    subject = f"{config.BUSINESS_NAME} Welcome"
    title = "Welcome"
    paragraphs = [
        f"Welcome to {config.BUSINESS_NAME}.",
        f"Please activate your account with the following URL: {verification_url}",
        "You can sign in after your account has been activated.",
    ]

    html = render_email(title=title, paragraphs=paragraphs, show_unsubscribe=False)
    send_email([to], subject, html)


def send_new_password(
    to: str,
    reset_url: str,
) -> None:
    subject = f"{config.BUSINESS_NAME} Password"
    title = "Password"
    paragraphs = [
        "We have received a request to reset your account password. "
        "If this was not requested by you or if this was a mistake, "
        "please ignore this email and we won't make any changes.",
        f"To reset your password, please visit the following url: {reset_url}.",
    ]

    html = render_email(title=title, paragraphs=paragraphs, show_unsubscribe=False)
    send_email([to], subject, html)
