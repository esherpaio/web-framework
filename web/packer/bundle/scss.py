import sass

from web.logger import log

from ..purge import CssPurgeConfig, CssPurger
from .css import CssBundle


class ScssBundle:
    OUT_EXT = ".css"

    def __init__(
        self,
        in_path: str,
        build_path: str | None = None,
        purge: CssPurgeConfig | None = None,
    ) -> None:
        self._in_path = in_path
        self._build_paths = [] if build_path is None else [build_path]
        self._purge = purge

    def compile(self) -> str:
        scss = sass.compile(
            filename=self._in_path,
            output_style="compressed",
            include_paths=self._build_paths,
        )
        bytes_before = len(scss.encode("utf-8"))
        if self._purge is not None:
            purge = CssPurger(self._purge).purge(scss)
            scss = purge.css

        compiled = CssBundle._compile(scss)
        bytes_after = len(compiled.encode("utf-8"))
        reduction = round((1 - bytes_after / bytes_before) * 100) if bytes_before else 0
        log.info(f"Compiled SCSS: {bytes_after / 1024:.2f} KB ({reduction}% reduction)")
        return compiled
