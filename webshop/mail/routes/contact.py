from webshop import config
from webshop.mail.base import render_email, send_email


def send_contact(
    email: str,
    name: str,
    message: str,
    company: str | None = None,
    phone: str | None = None,
) -> None:
    subject = f"{config.BUSINESS_NAME} Contact"
    title = "Contact Form"
    paragraphs = [
        f"Email: {email}<br>Name: {name}<br>Company: {company}<br>Phone: {phone}",
        f"Message: {message}",
    ]

    html = render_email(title=title, paragraphs=paragraphs)
    send_email([config.EMAIL_TO], subject, html)


def send_contact_confirmation(
    to: str,
    message: str,
) -> None:
    subject = f"{config.BUSINESS_NAME} Contact"
    title = "Contact Form"
    paragraphs = [
        f"We have received your message and will get back to you as soon as possible.",
        f"Message: {message}",
    ]

    html = render_email(title=title, paragraphs=paragraphs)
    send_email([to], subject, html)
