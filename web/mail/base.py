import base64
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP

import jinja2
from sendgrid import Attachment, Mail, SendGridAPIClient

from web import config
from web.helper.logger import logger
from web.i18n.base import _
from web.mail.utils import file_to_str


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
    blob_path: str = None,
    blob_name: str = None,
) -> None:
    # Check environment variables
    from_ = config.EMAIL_OVERRIDE or config.BUSINESS_EMAIL
    if not from_:
        raise EnvironmentError("No email address is configured")

    # Create list of unique to-addresses
    to = list(set(to))

    # Send email
    if config.EMAIL_METHOD == "smtp":
        if not (
            config.SMTP_HOST
            and config.SMTP_PORT
            and config.SMTP_USERNAME
            and config.SMTP_PASSWORD
        ):
            raise EnvironmentError("SMTP is not configured")
        send_over_smtp(from_, to, subject, html, blob_path, blob_name)
    elif config.EMAIL_METHOD == "sendgrid":
        if not config.SENDGRID_KEY:
            raise EnvironmentError("SendGrid is not configured")
        send_over_sengrid(from_, to, subject, html, blob_path, blob_name)
    else:
        raise EnvironmentError("No email method is configured")


def send_over_smtp(
    from_: str,
    to: list[str],
    subject: str,
    html: str,
    blob_path: str = None,
    blob_name: str = None,
) -> None:
    # Build the message
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = from_
    body = MIMEText(html, "html")
    message.attach(body)

    # Add attachment
    if blob_path and blob_name:
        blob_str = file_to_str(blob_path)
        attachment = MIMEApplication(blob_str)
        attachment.add_header("Content-Disposition", "attachment", filename=blob_name)
        message.attach(attachment)

    # Send the message
    try:
        conn = SMTP(config.SMTP_HOST, port=config.SMTP_PORT, timeout=10)
        conn.set_debuglevel(False)
        conn.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        try:
            conn.sendmail(from_, to, message.as_string())
        finally:
            conn.quit()
    except Exception as error:
        logger.critical(error)


def send_over_sengrid(
    from_: str,
    to: list[str],
    subject: str,
    html: str,
    blob_path: str = None,
    blob_name: str = None,
) -> None:
    # Build the email
    mail = Mail(
        from_email=from_,
        to_emails=to,
        subject=subject,
        html_content=html,
    )

    # Add attachment
    if blob_path and blob_name:
        blob_str = file_to_str(blob_path, encode=True)
        attachment = Attachment(
            file_content=blob_str,
            file_name=blob_name,
            disposition="attachment",
        )
        mail.add_attachment(attachment)

    # Send the email
    try:
        sendgrid = SendGridAPIClient(config.SENDGRID_KEY)
        sendgrid.send(mail)
    except Exception as error:
        logger.critical(error)
