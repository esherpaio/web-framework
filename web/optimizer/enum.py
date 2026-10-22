from enum import StrEnum


class Encoding(StrEnum):
    BROTLI = "br"
    DEFLATE = "deflate"
    GZIP = "gzip"


class Minification(StrEnum):
    HTML = "html"
    XML = "xml"


class CacheStatus(StrEnum):
    HIT = "hit"
    MISS = "miss"


class G(StrEnum):
    CACHE_STATUS = "_optimizer_cache_status"
