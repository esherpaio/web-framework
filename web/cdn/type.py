from typing import Protocol, TypeVar

_SP = TypeVar("_SP", covariant=True)


class _SupportsRead(Protocol[_SP]):
    def read(self, __length: int = ...) -> _SP: ...
