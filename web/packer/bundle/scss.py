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
        if self._purge is not None:
            result = CssPurger(self._purge).purge(scss)
            compiled = CssBundle._compile(result.css)
            bytes_after = len(compiled.encode("utf-8"))
            log.info(f"Purged CSS from {result.bytes_before} to {bytes_after} bytes")
            if result.dynamic_references:
                log.warning(
                    "CSS purge found "
                    f"{len(result.dynamic_references)} unrestricted dynamic "
                    "class expressions; add their possible values to the safelist"
                )
            return compiled
        return CssBundle._compile(scss)
