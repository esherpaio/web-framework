import time
from collections import OrderedDict
from threading import Lock
from typing import NamedTuple

from flask import Response, make_response
from werkzeug.datastructures import Headers

from .enum import Encoding


class CacheKey(NamedTuple):
    path: str
    encoding: Encoding | None


class CachedResponse(NamedTuple):
    """An immutable snapshot, so requests never share a mutable response."""

    stored_at: float
    status_code: int
    headers: tuple[tuple[str, str], ...]
    data: bytes

    @classmethod
    def from_response(cls, response: Response) -> "CachedResponse":
        return cls(
            stored_at=time.monotonic(),
            status_code=response.status_code,
            headers=tuple(response.headers),
            data=response.get_data(as_text=False),
        )

    @property
    def size(self) -> int:
        return len(self.data) + sum(len(k) + len(v) for k, v in self.headers)

    def is_expired(self, max_age_s: int) -> bool:
        return time.monotonic() - self.stored_at >= max_age_s

    def to_response(self) -> Response:
        response = make_response(self.data, self.status_code)
        response.headers = Headers(self.headers)
        return response


class ResponseCache:
    """A thread-safe LRU cache whose byte budget counts response payloads only."""

    def __init__(self, max_age_s: int, max_bytes: int) -> None:
        self._max_age_s = max_age_s
        self._max_bytes = max_bytes
        self._entries: OrderedDict[CacheKey, CachedResponse] = OrderedDict()
        self._size = 0
        self._lock = Lock()

    def get(self, key: CacheKey) -> Response | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.is_expired(self._max_age_s):
                self._remove(key)
                return None
            self._entries.move_to_end(key)
        return entry.to_response()

    def set(self, key: CacheKey, response: Response) -> bool:
        if self._max_age_s <= 0 or self._max_bytes <= 0:
            return False
        entry = CachedResponse.from_response(response)
        with self._lock:
            self._remove(key)
            if entry.size > self._max_bytes:
                return False
            self._entries[key] = entry
            self._size += entry.size
            self._evict()
        return True

    def delete(self, key: CacheKey) -> None:
        with self._lock:
            self._remove(key)

    def clear(self) -> bool:
        with self._lock:
            was_populated = bool(self._entries)
            self._entries.clear()
            self._size = 0
        return was_populated

    def _remove(self, key: CacheKey) -> None:
        entry = self._entries.pop(key, None)
        if entry is not None:
            self._size -= entry.size

    def _evict(self) -> None:
        while self._size > self._max_bytes:
            _, entry = self._entries.popitem(last=False)
            self._size -= entry.size
