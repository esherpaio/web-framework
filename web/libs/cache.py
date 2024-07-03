from typing import Any

from web.libs.utils import Singleton

#
# Classes
#


class Cache(dict, metaclass=Singleton):
    """A simple in-memory cache mechanism."""

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
