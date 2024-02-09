import zlib
from typing import Any, Callable

from flask import request
from werkzeug import Response

from web import config
from web.libs.logger import log

#
# Classes
#


class Cache(dict):
    """A simple cache mechanism for routes and objects."""

    def route(self, f: Callable) -> Callable[..., Response | str]:
        """Cache decorator for a route."""

        def wrap(*args, **kwargs) -> Response | str:
            if request.url in self:
                compressed = self[request.url]
                response = zlib.decompress(compressed).decode()
                return response

            log.info(f"Cache miss: {request.url}")
            response = f(*args, **kwargs)
            if config.APP_CACHE:
                try:
                    compressed = zlib.compress(response.encode())
                except AttributeError:
                    log.warning(f"Cache could not compress: {request.url}")
                    pass
                else:
                    self[request.url] = compressed
                    log.info(f"Cache set: {request.url}")
            return response

        wrap.__name__ = f.__name__
        return wrap

    def delete_urls(self) -> None:
        """Delete cached urls."""
        for key in self.copy().keys():
            if key.startswith("http"):
                del self[key]

    def __setattr__(self, key: str, value: Any) -> None:
        """Set a cache object."""
        self[key] = value

    def __getattr__(self, key: str) -> Any:
        """Get a cached object."""
        if key not in self:
            raise KeyError
        return self[key]


#
# Variables
#

cache = Cache()
