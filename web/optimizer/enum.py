from enum import StrEnum


class Encoding(StrEnum):
    brotli = "br"
    deflate = "deflate"
    gzip = "gzip"


class Minification(StrEnum):
    html = "html"
