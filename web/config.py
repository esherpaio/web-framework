import importlib
import os
from functools import cached_property
from typing import Any


class Config:
    _wrapped = None

    def __getattr__(self, name: str) -> Any:
        if self._wrapped is None:
            self._setup()
        return getattr(self._wrapped, name)

    def _setup(self) -> None:
        module_path = os.environ["APP_CONFIG_MODULE"]
        self._wrapped = importlib.import_module(module_path)


class EnvVar:
    def __init__(self, key: str, type_: Any, default: Any = None) -> None:
        self.key = key
        self.type_ = type_
        self.default = default

    @cached_property
    def value(self) -> Any:
        return self.parse(os.getenv(self.key, self.default))

    def parse(self, value: str) -> Any:
        if self.type_ is str:
            return value
        if self.type_ is int:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        if self.type_ is bool:
            return value in ["true", "1"]


config = Config()
