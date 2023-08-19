import zlib
from typing import Any, Callable

from flask import request
from werkzeug import Response

#
# Classes
#


class Cache(dict):
    """A simple cache mechanism for routes and objects."""

    def route(self, f: Callable) -> Callable[..., Response | str]:
        def wrap(*args, **kwargs) -> Response | str:
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

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __getattr__(self, key: str) -> Any:
        if key not in self:
            raise KeyError
        return self[key]


#
# Variables
#

cache = Cache()
