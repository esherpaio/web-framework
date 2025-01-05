import logging
from enum import StrEnum
from logging import Handler, LogRecord

from web.config import config

#
# Formatters
#


class _AnsiCode(StrEnum):
    DEBUG = "\x1b[37m"
    INFO = "\x1b[37m"
    WARNING = "\x1b[33m"
    ERROR = "\x1b[31m"
    CRITICAL = "\x1b[31m"
    RESET = "\x1b[0m"


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _AnsiCode[record.levelname]
        template = f"{color}%(levelname)s | %(message)s{_AnsiCode.RESET}"
        formatter = logging.Formatter(template)
        return formatter.format(record)


class HtmlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        template = "%(levelname)s | %(message)s"
        formatter = logging.Formatter(template)
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
        self.setLevel(logging.ERROR)
        self.setFormatter(HtmlFormatter())

    def emit(self, record: LogRecord) -> None:
        from web.mail import send_email

        try:
            send_email(
                subject=f"{config.WEBSITE_NAME} website error",
                html=self.format(record),
                to=[config.EMAIL_ADMIN],
            )
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


#
# Logger
#


def _get_logger(name: str) -> logging.Logger:
    base = logging.getLogger(name)
    base.setLevel(config.APP_LOG_LEVEL)
    stream = logging.StreamHandler()
    stream.setFormatter(PlainFormatter())
    base.addHandler(stream)
    if not config.APP_DEBUG and config.EMAIL_METHOD == "SMTP" and config.EMAIL_ADMIN:
        mail = MailHandler()
        base.addHandler(mail)
    return base


log = _get_logger(__name__)
