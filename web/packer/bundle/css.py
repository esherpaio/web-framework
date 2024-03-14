import os

# import re
import rcssmin


class CssBundle:
    ENCODING = "utf-8"
    IN_EXTS = [".css"]
    OUT_EXT = ".css"

    def __init__(self, in_dir: str, follow_subdirs: bool = True) -> None:
        self._in_dir = in_dir
        self._follow_subdirs = follow_subdirs

    def compile(self) -> str:
        compiled = ""
        for subdir, _, fns in os.walk(self._in_dir):
            for fn in fns:
                if not any([fn.endswith(ext) for ext in self.IN_EXTS]):
                    continue
                path = os.path.join(subdir, fn)
                content = open(path, "r", encoding=self.ENCODING).read()
                compiled += self._compile(content)
            if not self._follow_subdirs:
                break
        return compiled

    @staticmethod
    def _compile(css: str) -> str:
        return rcssmin.cssmin(css, keep_bang_comments=False)
