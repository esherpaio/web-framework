import sass

from .css import CssBundle


class ScssBundle:
    OUT_EXT = ".css"

    def __init__(self, in_path: str, extra_paths: list[str] | None = None) -> None:
        self._in_path = in_path
        if extra_paths is None:
            extra_paths = []
        self._extra_paths = extra_paths

    def compile(self) -> str:
        scss = sass.compile(
            filename=self._in_path,
            output_style="compressed",
            include_paths=self._extra_paths,
        )
        return CssBundle._compile(scss)
