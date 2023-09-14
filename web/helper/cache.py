import zlib
from typing import Any, Callable

from flask import request
from werkzeug import Response

from web import config
from web.helper.logger import logger

#
# Classes
#


class Cache(dict):
    """A simple cache mechanism for routes and objects."""

    def route(self, f: Callable) -> Callable[..., Response | str]:
        """Cache a route."""

        def wrap(*args, **kwargs) -> Response | str:
            if request.url in self:
                compressed = self[request.url]
                response = zlib.decompress(compressed).decode()
                return response

            response = f(*args, **kwargs)
            if not config.APP_DEBUG:
                compressed = zlib.compress(response.encode())
                self[request.url] = compressed
            return response

        wrap.__name__ = f.__name__
        return wrap

    def delete_routes(self) -> None:
        """Delete all cached routes."""
        logger.info("Removing cache routes")
        for key in self.copy().keys():
            if key.startswith("http"):
                del self[key]

    def __setattr__(self, key: str, value: Any) -> None:
        """Cache an object."""
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
