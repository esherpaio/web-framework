import os
from typing import Generator

import rjsmin


class JsBundle(object):
    ENCODING = "utf-8"
    IN_EXTS = [".js"]
    OUT_EXT = ".js"

    def __init__(self, in_path: str, subdirs: bool = True) -> None:
        self._in_path = in_path
        self._subdirs = subdirs

    def compile(self) -> str:
        compiled = ""
        for path in self.iter_paths():
            content = open(path, "r", encoding=self.ENCODING).read()
            compiled += self._compile(content)
        return compiled

    @staticmethod
    def _compile(css: str) -> str:
        return rjsmin.jsmin(css, keep_bang_comments=False) + "\n"

    def iter_paths(self) -> Generator[str, None, None]:
        if os.path.isfile(self._in_path):
            if any([self._in_path.endswith(ext) for ext in self.IN_EXTS]):
                yield self._in_path
            return
        if os.path.isdir(self._in_path):
            for subdir, _, fns in os.walk(self._in_path):
                for fn in fns:
                    if any([fn.endswith(ext) for ext in self.IN_EXTS]):
                        yield os.path.join(subdir, fn)
                if not self._subdirs:
                    break
