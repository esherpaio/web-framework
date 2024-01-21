import os

from rjsmin import jsmin


class JsBundle(object):
    ENCODING = "utf-8"
    IN_EXTS = [".js"]
    OUT_EXT = ".js"

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
                compiled += jsmin(content)
            if not self._follow_subdirs:
                break
        return compiled
