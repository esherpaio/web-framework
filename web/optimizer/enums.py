from enum import StrEnum

from werkzeug.datastructures import Headers


class Encoding(StrEnum):
    brotli = "br"
    deflate = "deflate"
    gzip = "gzip"


class Minification(StrEnum):
    html = "html"


def get_encoding(headers: Headers) -> Encoding | None:
    if headers is None:
        return None
    encoding = headers.get("Accept-Encoding", "").lower()
    if "br" in encoding:
        return Encoding.brotli
    if "deflate" in encoding:
        return Encoding.deflate
    if "gzip" in encoding:
        return Encoding.gzip
    return None


def get_minification(mimetype: str | None) -> Minification | None:
    if mimetype is None:
        return None
    if mimetype.endswith("html"):
        return Minification.html
    return None
