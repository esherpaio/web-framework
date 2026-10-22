from typing import Callable

from .enum import Minification
from .object import minify_html, minify_xml

_MINIFIERS: dict[Minification, Callable[[str], str]] = {
    Minification.HTML: minify_html,
    Minification.XML: minify_xml,
}


def minification_for(mimetype: str | None) -> Minification | None:
    if mimetype is None:
        return None
    return next((x for x in _MINIFIERS if mimetype.endswith(x)), None)


def minify(text: str, minification: Minification) -> str:
    return _MINIFIERS[minification](text)
