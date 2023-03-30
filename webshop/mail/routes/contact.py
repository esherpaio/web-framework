from webshop import config
from webshop.mail.base import render_email, send_email


def send_contact(
    email: str,
    name: str,
    message: str,
    company: str | None = None,
    phone: str | None = None,
) -> None:
    subject = "Costronica Contact"
    title = "Contact Form"
    paragraphs = [
        f"Email: {email}<br>Name: {name}<br>Company: {company}<br>Phone: {phone}",
        f"Message: {message}",
    ]

    html = render_email(title=title, paragraphs=paragraphs)
    send_email(config.BUSINESS_EMAIL, subject, html)
