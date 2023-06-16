import base64
import os
from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP

import jinja2
from sendgrid import Attachment, Mail, SendGridAPIClient

from web import config
from web.helper.logger import logger
from web.i18n.base import _


def render_email(
    title: str,
    paragraphs: list[str],
    **kwargs,
) -> str:
    curr_dir = os.path.dirname(os.path.realpath(__file__))

    # Add CSS and config to kwargs
    css_path = os.path.join(curr_dir, "template", "template.css")
    with open(css_path, "r") as file:
        css = file.read()
    kwargs.update(
        {
            "css": css,
            "config": config,
            "title": title,
            "paragraphs": paragraphs,
        }
    )

    # Render with Jinja2
    loader = jinja2.FileSystemLoader(curr_dir)
    environment = jinja2.Environment(loader=loader)
    html_path = "template/template.html"  # Jinja requires relative path
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
    if not config.BUSINESS_EMAIL:
        raise EnvironmentError("Variable `BUSINESS_EMAIL` is not set")
    # Create list of unique to-addresses
    to = list(set(to))
    # Try to send over SMTP
    if (
        config.SMTP_HOST
        and config.SMTP_PORT
        and config.SMTP_USERNAME
        and config.SMTP_PASSWORD
    ):
        _send_over_smtp(to, subject, html)
    # Try to send over SendGrid
    elif config.SENDGRID_KEY:
        _send_over_sengrid(to, subject, html, blob_str, blob_name, blob_type)
    # No email sending method is configured
    else:
        raise EnvironmentError("No email sending method is configured")


def _send_over_smtp(
    to: list[str],
    subject: str,
    html: str,
) -> None:
    # Build the message
    msg = MIMEText(html, _subtype="html")
    msg["Subject"] = subject
    msg["From"] = config.BUSINESS_EMAIL

    # Send the message
    try:
        conn = SMTP(host=config.SMTP_HOST, port=config.SMTP_PORT)
        conn.set_debuglevel(False)
        conn.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        try:
            conn.sendmail(config.BUSINESS_EMAIL, to, msg.as_string())
        finally:
            conn.quit()
    except Exception as error:
        logger.critical(error)


def _send_over_sengrid(
    to: list[str],
    subject: str,
    html: str,
    blob_str: str = None,
    blob_name: str = None,
    blob_type: str = None,
) -> None:
    # Create an email
    mail = Mail(
        from_email=config.BUSINESS_EMAIL,
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
