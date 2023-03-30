import re


def is_email(text: str) -> bool:
    match = re.match(r"[^@]+@[^@]+\.[^@]+", text)
    return bool(match)


def is_phone(text: str) -> bool:
    match = re.match(r"(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
    return bool(match)


def gen_slug(name: str) -> str:
    name = re.sub(r"[^\w -]+", "", name)
    name = re.sub(r"[ _]+", "-", name)
    name = name.lower()
    return name
