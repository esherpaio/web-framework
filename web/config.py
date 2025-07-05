import importlib
import os
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


config = Config()
