import logging
from enum import StrEnum
from logging import Handler, LogRecord

from web.config import config

#
# Formatters
#


class AnsiFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _AnsiCode[record.levelname]
        string = f"{color}%(levelname)s | %(message)s{_AnsiCode.RESET}"
        formatter = logging.Formatter(string)
        return formatter.format(record)


class _AnsiCode(StrEnum):
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


#
# Handlers
#


class MailHandler(Handler):
    def __init__(self) -> None:
        super().__init__()
        self.setLevel(logging.ERROR)
        self.setFormatter(PlainFormatter())

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
    level = logging.DEBUG if config.APP_DEBUG else logging.INFO
    base = logging.getLogger(name)
    base.setLevel(level)
    stream = logging.StreamHandler()
    stream.setFormatter(AnsiFormatter())
    base.addHandler(stream)
    if not config.APP_DEBUG and config.EMAIL_METHOD == "SMTP" and config.EMAIL_ADMIN:
        mail = MailHandler()
        base.addHandler(mail)
    return base


log = _get_logger(__name__)
