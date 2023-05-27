import zlib
from typing import Callable

from flask import Response, request

from web.helper.operator import Singleton

CACHE_MIMETYPE = [
    ("text/css", 31536000),
    ("application/javascript", 31536000),
    ("font/woff2", 31536000),
]


class Cache(dict, metaclass=Singleton):
    def route(self, f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            if request.full_path in self:
                compressed = self[request.full_path]
                response = zlib.decompress(compressed).decode()
                return Response(response)

            response = f(*args, **kwargs)
            compressed = zlib.compress(response.encode())
            self[request.full_path] = compressed
            return response

        wrap.__name__ = f.__name__
        return wrap

    def __setattr__(self, key: str, value: any) -> None:
        self[key] = value

    def __getattr__(self, key: str) -> any:
        if key not in self:
            raise KeyError
        return self[key]


cache = Cache()
