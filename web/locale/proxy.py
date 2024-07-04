from typing import Any

from flask import g, has_request_context
from werkzeug.local import LocalProxy

from .locale import Locale


def _get_proxy_locale() -> Locale | None:
    if has_request_context():
        if "_locale" not in g:
            g._locale = Locale()
        return g._locale
    return None


current_locale: Any = LocalProxy(lambda: _get_proxy_locale())
