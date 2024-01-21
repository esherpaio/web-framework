import sass

from web.packer.bundle import CssBundle


class ScssBundle:
    OUT_EXT = ".scss"

    def __init__(self, in_path: str) -> None:
        self._in_path = in_path

    def compile(self) -> str:
        scss = sass.compile(filename=self._in_path, output_style="compressed")
        compiled = CssBundle._compile(scss)
        return compiled
