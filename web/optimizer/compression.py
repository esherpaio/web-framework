import gzip
import zlib
from functools import partial
from typing import Callable

import brotli

from .enum import Encoding

_COMPRESSORS: dict[Encoding, Callable[[bytes], bytes]] = {
    Encoding.BROTLI: partial(brotli.compress, quality=11),
    Encoding.DEFLATE: partial(zlib.compress, level=9),
    Encoding.GZIP: partial(gzip.compress, compresslevel=9),
}


def negotiate_encoding(accept_encoding: str) -> Encoding | None:
    accepted = accept_encoding.lower()
    return next((x for x in _COMPRESSORS if x in accepted), None)


def compress(data: bytes, encoding: Encoding) -> bytes:
    return _COMPRESSORS[encoding](data)
