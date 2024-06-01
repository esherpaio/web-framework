from typing import Any

#
# Classes
#


class Cache(dict):
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
