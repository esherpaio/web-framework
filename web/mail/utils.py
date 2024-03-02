import email.utils
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import StrEnum
from smtplib import SMTP_SSL

import jinja2

from web.config import config
from web.libs.logger import log

#
# Classes
#


class MailMethod(StrEnum):
    SMTP = "SMTP"


#
# Functions
#


def render_email(name: str = "default", **attrs) -> str:
    dir_ = os.path.dirname(os.path.realpath(__file__))
    loader = jinja2.FileSystemLoader(dir_)
    environment = jinja2.Environment(loader=loader)
    fp = os.path.join("template", f"{name}.html")
    attrs.update({"config": config})
    html = environment.get_template(fp).render(attrs)
    return html


def send_email(
    subject: str,
    html: str,
    to: list[str] | None = None,
    reply_to: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    blob_path: str | None = None,
    blob_name: str | None = None,
) -> bool:
    # Make unique addresses
    if to is not None:
        to = list(set(to))
    if cc is not None:
        cc = list(set(cc))
    if bcc is not None:
        bcc = list(set(bcc))
    # Send email
    if config.EMAIL_METHOD == MailMethod.SMTP:
        _send_email_smtp(subject, html, to, reply_to, cc, bcc, blob_path, blob_name)
    else:
        log.error(f"Cannot send email, unknown method {config.EMAIL_METHOD}".strip())
        return False
    return True


def _send_email_smtp(
    subject: str,
    html: str,
    to: list[str] | None = None,
    reply_to: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    blob_path: str | None = None,
    blob_name: str | None = None,
) -> None:
    # Create message
    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_FROM
    msg["Reply-To"] = reply_to or config.EMAIL_FROM
    msg["Subject"] = subject
    msg["Date"] = email.utils.localtime()
    if to is not None:
        msg["To"] = ",".join(to)
    if cc is not None:
        msg["Cc"] = ",".join(cc)
    if bcc is not None:
        msg["Bcc"] = ",".join(bcc)
    # Add body
    body = MIMEText(html, "html")
    msg.attach(body)
    # Add attachment
    if blob_path and blob_name:
        with open(blob_path, "rb") as file_:
            data = file_.read()
        attachment = MIMEApplication(data)
        attachment.add_header("Content-Disposition", "attachment", filename=blob_name)
        msg.attach(attachment)
    # Send email
    conn = SMTP_SSL(config.SMTP_HOST, port=config.SMTP_PORT, timeout=20)
    conn.set_debuglevel(False)
    conn.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
    conn.send_message(msg)
    conn.quit()
