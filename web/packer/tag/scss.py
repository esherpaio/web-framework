import sass

from web.packer.tag import CssPacker


class ScssPacker:
    ENCODING = "utf-8"
    IN_EXTS = [".css"]
    OUT_EXT = ".css"

    def __init__(self, in_path: str) -> None:
        self._in_path = in_path

    def compile(self) -> str:
        scss = sass.compile(filename=self._in_path, output_style="compressed")
        compiled = CssPacker._compile(scss)
        return compiled
