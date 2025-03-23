from typing import cast

from flask import g, has_request_context
from werkzeug.local import LocalProxy

from .locale import Locale


def _get_proxy_locale() -> Locale:
    if has_request_context():
        if "_locale" not in g:
            g._locale = Locale()
        return g._locale
    return Locale()


current_locale = cast(Locale, LocalProxy(lambda: _get_proxy_locale()))
