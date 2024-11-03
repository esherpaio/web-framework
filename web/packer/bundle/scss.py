import sass

from .css import CssBundle


class ScssBundle:
    OUT_EXT = ".css"

    def __init__(self, in_path: str, build_path: str | None = None) -> None:
        self._in_path = in_path
        self._build_paths = [] if build_path is None else [build_path]

    def compile(self) -> str:
        scss = sass.compile(
            filename=self._in_path,
            output_style="compressed",
            include_paths=self._build_paths,
        )
        return CssBundle._compile(scss)
