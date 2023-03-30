import logging
from enum import StrEnum


class AnsiCode(StrEnum):
    DEBUG = "\x1b[37m"
    INFO = "\x1b[37m"
    WARNING = "\x1b[33m"
    ERROR = "\x1b[31m"
    CRITICAL = "\x1b[31m"


class Formatter(logging.Formatter):
    RESET = "\x1b[0m"
    FORMAT = "%(levelname)s | %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        color = AnsiCode[record.levelname]
        string = f"{color}{self.FORMAT}{self.RESET}"
        record.levelname = record.levelname
        formatter = logging.Formatter(string)
        return formatter.format(record)


def get_logger(name: str) -> logging.Logger:
    stream = logging.StreamHandler()
    stream.setFormatter(Formatter())
    base = logging.getLogger(name)
    base.setLevel(logging.DEBUG)
    base.addHandler(stream)
    return base


logger = get_logger(__name__)
