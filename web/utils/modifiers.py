import re
import urllib.parse
from urllib.parse import urlparse, urlunparse

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")


def normalize_url(url: str, scheme: str = "https") -> str:
    url = url.strip()
    if not _SCHEME_RE.match(url):
        url = f"{scheme}://{url}"
    parts = urlparse(url)
    return urlunparse(parts)


def strip_scheme(url: str) -> str:
    url_parsed = urllib.parse.urlparse(url)
    scheme = f"{url_parsed.scheme}://"
    return url_parsed.geturl().replace(scheme, "", 1)


def replace_domain(in_url: str, new_domain: str) -> str:
    new_domain = strip_scheme(new_domain)
    in_url_parsed = urllib.parse.urlparse(in_url)
    new_url_parsed = in_url_parsed._replace(netloc=new_domain)
    return urllib.parse.urlunparse(new_url_parsed)
