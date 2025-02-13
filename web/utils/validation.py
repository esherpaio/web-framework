import re

from phonenumbers.phonenumberutil import _is_viable_phone_number


def is_email(text: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


def is_phone(text: str) -> bool:
    return _is_viable_phone_number(text)
