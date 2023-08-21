import logging
from enum import StrEnum

#
# Classes
#


class AnsiCode(StrEnum):
    """ANSI escape codes for colored logging."""

    DEBUG = "\x1b[37m"
    INFO = "\x1b[37m"
    WARNING = "\x1b[33m"
    ERROR = "\x1b[31m"
    CRITICAL = "\x1b[31m"
    RESET = "\x1b[0m"


class Formatter(logging.Formatter):
    """A custom logging formatter."""

    def format(self, record: logging.LogRecord) -> str:
        color = AnsiCode[record.levelname]
        string = f"{color}%(levelname)s | %(message)s{AnsiCode.RESET}"
        record.levelname = record.levelname
        formatter = logging.Formatter(string)
        return formatter.format(record)


#
# Functions
#


def get_logger(name: str) -> logging.Logger:
    """Get a logger."""

    base = logging.getLogger(name)
    base.setLevel(logging.DEBUG)
    stream = logging.StreamHandler()
    stream.setFormatter(Formatter())
    base.addHandler(stream)
    return base


# Variables


logger = get_logger(__name__)
