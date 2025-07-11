import gzip
import zlib
from typing import Callable

import brotli
from flask import Flask, Response, make_response, request
from werkzeug.datastructures import Headers

from web.cache import cache
from web.config import config
from web.logger import log
from web.utils import Singleton

from .enum import Encoding, Minification
from .object import minify_html


class Optimizer(metaclass=Singleton):
    ENCODING = "utf-8"

    def __init__(self, app: Flask | None = None) -> None:
        self._cached_endpoints: set[str] = set()
        if app is not None:
            self.init(app)

    def init(self, app: Flask) -> None:
        app.after_request(self.after_request)

    #
    # Minification
    #

    def execute_minify(
        cls, response: Response, minification: Minification | None
    ) -> None:
        # get data
        response.direct_passthrough = False
        text = response.get_data(as_text=True)
        # minify
        if minification == Minification.html:
            minified = minify_html(text)
        else:
            raise ValueError
        # set data
        log.debug(f"Optimizer minified {request.full_path}")
        encoded = minified.encode(cls.ENCODING)
        response.set_data(encoded)

    @staticmethod
    def get_minification(mimetype: str | None) -> Minification | None:
        if mimetype is None:
            return None
        if mimetype.endswith("html"):
            return Minification.html
        return None

    #
    # Compression
    #

    def execute_compress(cls, response: Response, encoding: Encoding | None) -> None:
        # get data
        response.direct_passthrough = False
        data = response.get_data(as_text=False)
        # get level
        level = cls.get_compress_level(encoding)
        if level is None:
            return
        # compress
        if encoding == Encoding.brotli:
            compressed_data = brotli.compress(data, quality=level)
        elif encoding == Encoding.deflate:
            compressed_data = zlib.compress(data, level=level)
        elif encoding == Encoding.gzip:
            compressed_data = gzip.compress(data, compresslevel=level)
        else:
            raise ValueError
        # set data
        log.debug(f"Optimizer compressed {request.full_path}")
        response.set_data(compressed_data)

    @staticmethod
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

    @staticmethod
    def get_compress_level(encoding: Encoding | None) -> int | None:
        if encoding == Encoding.gzip:
            return 9
        if encoding == Encoding.brotli:
            return 11
        if encoding == Encoding.deflate:
            return 9
        return None

    #
    # Optimization
    #

    def optimize_response(
        cls,
        response: Response,
        encoding: Encoding | None,
        minification: Minification | None,
    ) -> None:
        if isinstance(minification, Minification):
            cls.execute_minify(response, minification)
        if isinstance(encoding, Encoding):
            cls.execute_compress(response, encoding)

    #
    # Headers
    #

    @staticmethod
    def set_headers(response: Response, encoding: Encoding | None) -> None:
        if response.direct_passthrough:
            return
        if isinstance(encoding, Encoding):
            response.headers["Content-Encoding"] = encoding
        response.headers["Content-Length"] = str(response.content_length)

    #
    # Cache
    #

    def set_cache(self, response: Response, encoding: Encoding | None) -> None:
        if request.endpoint not in self._cached_endpoints:
            return
        log.info(f"Optimizer cached {request.full_path}")
        cache[(request.full_path, encoding)] = response.get_data(as_text=False)

    def get_cache(self, encoding: Encoding | None) -> Response | None:
        if isinstance(request.endpoint, str):
            self._cached_endpoints.add(request.endpoint)
        from_cache = cache.get((request.full_path, encoding))
        if from_cache is not None:
            response = make_response()
            response.direct_passthrough = False
            response.set_data(from_cache)
            return response
        return None

    def del_cache(self) -> None:
        for key in list(cache.keys()):
            if (
                isinstance(key, tuple)
                and isinstance(key[0], str)
                and key[0].startswith("/")
            ):
                del cache[key]
        self._cached_endpoints = set()

    #
    # Request handler
    #

    def cache(self, f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            if config.APP_OPTIMIZE:
                encoding = self.get_encoding(request.headers)
                response = self.get_cache(encoding)
                if response is not None:
                    self.set_headers(response, encoding)
                    return response
            return f(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    def after_request(self, response: Response) -> Response:
        # validate response
        if not config.APP_OPTIMIZE:
            return response
        if response.status_code is None or response.content_length is None:
            return response
        if response.status_code < 200 or response.status_code >= 300:
            return response
        if "Content-Encoding" in response.headers:
            return response
        # choose encoding and minification
        encoding = self.get_encoding(request.headers)
        minification = self.get_minification(response.mimetype)
        if encoding is None and minification is None:
            return response
        # handle response
        self.optimize_response(response, encoding, minification)
        self.set_cache(response, encoding)
        self.set_headers(response, encoding)
        return response


optimizer = Optimizer()
