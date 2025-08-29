import logging
import re
from logging import Handler, LogRecord

from web.setup import config

#
# Filters and formatters
#


LEVEL_COLORS = {
    "DEBUG": "\033[90m",
    "INFO": "",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[41m",
}
RESET = "\033[0m"


class WerkzeugFilter(logging.Filter):
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    pattern = re.compile(r'"(\S+)\s+(\S+)[^"]*"\s+(\d{3})')

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        escaped = self.ansi_escape.sub("", message)
        match = self.pattern.search(escaped)
        if match:
            color = LEVEL_COLORS.get(record.levelname, "")
            method, url, status = match.groups()
            record.msg = f"{color}{method} {url} {status}{RESET}"
            record.args = ()
        return True


class PlainFormatter(logging.Formatter):
    template = "%(message)s"

    def format(self, record: logging.LogRecord) -> str:
        formatter = logging.Formatter(self.template)
        color = LEVEL_COLORS.get(record.levelname, "")
        message = formatter.format(record)
        return f"{color}{message}{RESET}"


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
