import re
import urllib.parse

#
# Functions
#


def is_email(text: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


def is_phone(text: str) -> bool:
    return bool(re.match(r"(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text))


def gen_slug(name: str) -> str:
    return re.sub(r"[ _]+", "-", re.sub(r"[^\w -]+", "", name)).lower()


def strip_scheme(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    scheme = f"{parsed.scheme}://"
    return parsed.geturl().replace(scheme, "", 1)
