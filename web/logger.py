import logging
from enum import Enum
from logging import Handler, LogRecord

from web.setup import config

#
# Enums
#


class AnsiColor(Enum):
    DEBUG = 90
    WARNING = 33
    ERROR = 31
    CRITICAL = 41


#
# Formatters
#


class PlainFormatter(logging.Formatter):
    template = "%(message)s"

    def format(self, record: logging.LogRecord) -> str:
        formatter = logging.Formatter(self.template)
        message = formatter.format(record)
        try:
            color_int = AnsiColor[record.levelname].value
        except KeyError:
            return message
        return f"\x1b[{color_int}m{message}\x1b[0m"


class HtmlFormatter(logging.Formatter):
    template = "%(message)s"

    def format(self, record: logging.LogRecord) -> str:
        formatter = logging.Formatter(self.template)
        message = formatter.formatMessage(record)
        if record.exc_info:
            exception = self.formatException(record.exc_info)
            message += f"<br><pre>{exception}</pre>"
        return message


#
# Handlers
#


class MailHandler(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.setLevel(config.MAIL_LOG_LEVEL)
        self.setFormatter(HtmlFormatter())

    def emit(self, record: LogRecord) -> None:
        from web.mail import send_email

        subject_parts = [config.MAIL_LOG_PREFIX, "website error"]
        subject_parts = [x for x in subject_parts if x]
        subject = " ".join(subject_parts)
        html = self.format(record)

        try:
            send_email(subject, html, to=[config.MAIL_ADMIN])
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


#
# Logger
#


def _get_logger(name: str) -> logging.Logger:
    base = logging.getLogger(name)
    base.setLevel(config.LOG_LEVEL)
    stream = logging.StreamHandler()
    stream.setFormatter(PlainFormatter())
    base.addHandler(stream)
    if not config.MAIL_LOG_ENABLED and config.MAIL_ADMIN:
        mail = MailHandler()
        base.addHandler(mail)
    return base


log = _get_logger(__name__)
