import logging
import smtplib
from email.message import EmailMessage
from enum import StrEnum
from logging.handlers import SMTPHandler as _SMTPHandler
from smtplib import SMTP_SSL

from web.config import config

#
# Classes
#


class _AnsiCode(StrEnum):
    """ANSI escape codes."""

    DEBUG = "\x1b[37m"
    INFO = "\x1b[37m"
    WARNING = "\x1b[33m"
    ERROR = "\x1b[31m"
    CRITICAL = "\x1b[31m"
    RESET = "\x1b[0m"


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        string = "%(levelname)s | %(message)s"
        formatter = logging.Formatter(string)
        return formatter.format(record)


class AnsiFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _AnsiCode[record.levelname]
        string = f"{color}%(levelname)s | %(message)s{_AnsiCode.RESET}"
        formatter = logging.Formatter(string)
        return formatter.format(record)


class SMTPHandler(_SMTPHandler):
    def __init__(self) -> None:
        super().__init__(
            mailhost=(config.SMTP_HOST, config.SMTP_PORT),
            credentials=(config.SMTP_USERNAME, config.SMTP_PASSWORD),
            fromaddr=config.EMAIL_FROM,
            toaddrs=[config.EMAIL_ADMIN],
            subject=f"{config.WEBSITE_NAME} website error",
        )
        self.setLevel(logging.ERROR)
        self.setFormatter(PlainFormatter())

    def emit(self, record):
        try:
            # Create message
            msg = EmailMessage()
            msg["From"] = self.fromaddr
            msg["To"] = ",".join(self.toaddrs)
            msg["Subject"] = self.getSubject(record)
            msg.set_content(self.format(record))
            # Send email
            port = self.mailport or smtplib.SMTP_PORT
            conn = SMTP_SSL(self.mailhost, port=port, timeout=25)
            if self.username and self.password:
                conn.login(self.username, self.password)
            conn.send_message(msg, self.fromaddr, self.toaddrs)
            conn.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


#
# Functions
#


def _get_logger(name: str) -> logging.Logger:
    level = logging.DEBUG if config.APP_DEBUG else logging.INFO
    base = logging.getLogger(name)
    base.setLevel(level)
    stream = logging.StreamHandler()
    stream.setFormatter(AnsiFormatter())
    base.addHandler(stream)
    if not config.APP_DEBUG and config.EMAIL_METHOD == "SMTP" and config.EMAIL_ADMIN:
        smtp = SMTPHandler()
        base.addHandler(smtp)
    return base


# Variables


log = _get_logger(__name__)
