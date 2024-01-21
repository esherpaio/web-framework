import os
import re


class CssPacker:
    ENCODING = "utf-8"
    IN_EXTS = [".css"]
    OUT_EXT = ".css"

    def __init__(self, in_dirs: list[str], follow_subdirs: bool = True) -> None:
        self._in_dirs = in_dirs
        self._follow_subdirs = follow_subdirs

    def compile(self) -> str:
        compiled = ""
        for in_dir in self._in_dirs:
            for subdir, _, fns in os.walk(in_dir):
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
        # remove comments
        css = re.sub(r"\s*/\*\s*\*/", "$$HACK1$$", css)  # preserve IE<6 comment hack
        css = re.sub(r"/\*[\s\S]*?\*/", "", css)
        css = css.replace("$$HACK1$$", "/**/")  # preserve IE<6 comment hack
        # spaces may be safely collapsed as generated content will collapse them anyway
        css = re.sub(r"\s+", " ", css)
        # shorten collapsable colors: #aabbcc to #abc
        css = re.sub(r"#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)", r"#\1\2\3\4", css)
        # fragment values can loose zeros
        css = re.sub(r":\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;", r":\1;", css)
        # strip css
        css = css.strip()
        return css
