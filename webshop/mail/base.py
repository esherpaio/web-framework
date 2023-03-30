import base64
import os

import jinja2
from sendgrid import Mail, Attachment, SendGridAPIClient

from webshop import config
from webshop.helper.logger import logger

_DIR = os.path.dirname(os.path.realpath(__file__))


def render_email(**kwargs) -> str:
    # Add CSS and config to kwargs.
    css_path = os.path.join(_DIR, "template", "template.css")
    with open(css_path, "r") as file:
        css = file.read()
    kwargs.update({"css": css})
    kwargs.update({"config": config})

    # Render with Jinja2.
    loader = jinja2.FileSystemLoader(_DIR)
    environment = jinja2.Environment(loader=loader)
    html_path = os.path.join(_DIR, "template", "template.html")
    html = environment.get_template(html_path).render(kwargs)

    return html


def send_email(
    to: list[str],
    subject: str,
    html: str,
    blob_str: str = None,
    blob_name: str = None,
    blob_type: str = None,
) -> None:
    # Check environment variables
    if config.EMAIL_FROM is None:
        raise EnvironmentError("Variable `EMAIL_FROM` is not set")
    if config.SENDGRID_KEY is None:
        raise EnvironmentError("Variable `SENDGRID_KEY` is not set")

    # Create list of unique to-addresses
    # Sendgrid does not allow duplicates
    to = list(set(to))

    # Create an email
    mail = Mail(
        from_email=config.EMAIL_FROM,
        to_emails=to,
        subject=subject,
        html_content=html,
    )

    # Add attachment
    if blob_str and blob_name and blob_type:
        attachment = Attachment(
            file_content=blob_str,
            file_name=blob_name,
            file_type=blob_type,
            disposition="attachment",
        )
        mail.add_attachment(attachment)

    # Send the email
    try:
        sendgrid = SendGridAPIClient(config.SENDGRID_KEY)
        sendgrid.send(mail)
    except Exception as error:
        logger.critical(error)


def pdf_to_string(path: str) -> str:
    with open(path, "rb") as file:
        data = file.read()
    return base64.b64encode(data).decode()
