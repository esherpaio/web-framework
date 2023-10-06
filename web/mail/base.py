import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP

import jinja2

from web import config
from web.helper.logger import logger
from web.mail.utils import file_to_str


def render_email(
    title: str,
    paragraphs: list[str],
    **kwargs,
) -> str:
    # Add CSS and config to kwargs
    dir_ = os.path.dirname(os.path.realpath(__file__))
    css_path = os.path.join(dir_, "template", "template.css")
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
    loader = jinja2.FileSystemLoader(dir_)
    environment = jinja2.Environment(loader=loader)
    html_path = "template/template.html"  # Jinja requires relative path
    html = environment.get_template(html_path).render(kwargs)
    return html


def send_email(
    to: list[str],
    subject: str,
    html: str,
    reply_to: str | None = None,
    blob_path: str | None = None,
    blob_name: str | None = None,
) -> None:
    # Create list of unique to-addresses
    to = list(set(to))
    # Send email
    if config.EMAIL_METHOD == "smtp":
        _send_smtp(config.EMAIL_FROM, to, subject, html, reply_to, blob_path, blob_name)
    else:
        logger.warning("Email not send because no valid method is configured")


def _send_smtp(
    from_: str,
    to: list[str],
    subject: str,
    html: str,
    reply_to: str | None = None,
    blob_path: str | None = None,
    blob_name: str | None = None,
) -> None:
    # Build the message
    msg = MIMEMultipart()
    msg["to"] = ",".join(to)
    msg["subject"] = subject
    msg["from"] = from_
    msg.add_header("reply-to", reply_to or from_)
    body = MIMEText(html, "html")
    msg.attach(body)
    # Add attachment
    if blob_path and blob_name:
        blob_str = file_to_str(blob_path)
        attachment = MIMEApplication(blob_str)
        attachment.add_header("Content-Disposition", "attachment", filename=blob_name)
        msg.attach(attachment)
    # Send the message
    conn = SMTP(config.SMTP_HOST, port=config.SMTP_PORT, timeout=10)
    conn.set_debuglevel(False)
    conn.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
    conn.sendmail(msg["from"], msg["to"], msg.as_string())
    conn.quit()
