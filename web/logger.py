import logging
from logging import Handler, LogRecord

from web.setup import config

#
# Formatters
#


class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        template = "[%(levelname)s] %(message)s"
        formatter = logging.Formatter(template)
        return formatter.format(record)


class HtmlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        template = "[%(levelname)s] %(message)s"
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
        self.setLevel(config.MAIL_LOG_LEVEL)
        self.setFormatter(HtmlFormatter())

    def emit(self, record: LogRecord) -> None:
        from web.mail import send_email

        if config.MAIL_LOG_PREFIX is None:
            subject = "Website error"
        else:
            subject = f"{config.MAIL_LOG_PREFIX} website error"

        try:
            send_email(
                subject=subject,
                html=self.format(record),
                to=[config.MAIL_ADMIN],
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
    base.setLevel(config.LOG_LEVEL)
    stream = logging.StreamHandler()
    stream.setFormatter(PlainFormatter())
    base.addHandler(stream)
    if not config.MAIL_LOG_ENABLED and config.MAIL_ADMIN:
        mail = MailHandler()
        base.addHandler(mail)
    return base


log = _get_logger(__name__)
