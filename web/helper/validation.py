import re

#
# Functions
#


def is_email(text: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


def is_phone(text: str) -> bool:
    return bool(re.match(r"(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text))


def gen_slug(name: str) -> str:
    return re.sub(r"[ _]+", "-", re.sub(r"[^\w -]+", "", name)).lower()
