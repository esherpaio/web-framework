from typing import Any

from flask import url_for as _url_for

from web.config import config


def url_for(
    endpoint: str,
    _anchor: str | None = None,
    _method: str | None = None,
    _scheme: str | None = None,
    _external: bool | None = None,
    **values: Any,
) -> str:
    print(1)
    if _scheme is not None:
        scheme = _scheme
    elif not config.APP_DEBUG:
        scheme = "https"
    else:
        scheme = "http"
    return _url_for(
        endpoint,
        _anchor=_anchor,
        _method=_method,
        _scheme=scheme,
        _external=_external,
        **values,
    )
