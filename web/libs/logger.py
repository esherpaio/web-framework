import logging
from enum import StrEnum

#
# Classes
#


class _AnsiCode(StrEnum):
    """ANSI escape codes for colored logging."""

    DEBUG = "\x1b[37m"
    INFO = "\x1b[37m"
    WARNING = "\x1b[33m"
    ERROR = "\x1b[31m"
    CRITICAL = "\x1b[31m"
    RESET = "\x1b[0m"


class Formatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _AnsiCode[record.levelname]
        string = f"{color}%(levelname)s | %(message)s{_AnsiCode.RESET}"
        formatter = logging.Formatter(string)
        return formatter.format(record)


#
# Functions
#


def _get_logger(name: str) -> logging.Logger:
    base = logging.getLogger(name)
    base.setLevel(logging.DEBUG)
    if base.hasHandlers():
        base.handlers.clear()
    stream = logging.StreamHandler()
    stream.setFormatter(Formatter())
    base.addHandler(stream)
    base.propagate = False
    return base


# Variables


log = _get_logger(__name__)
