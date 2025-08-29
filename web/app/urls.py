from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from flask import redirect, request
from flask import url_for as _url_for
from requests.models import PreparedRequest
from werkzeug import Response

from web.setup import config


def parse_url(
    endpoint: str,
    _func: Callable,
    _anchor: str | None = None,
    _method: str | None = None,
    _scheme: str | None = None,
    _external: bool | None = None,
    **values: Any,
) -> str:
    if endpoint.startswith(("http://", "https://")):
        req = PreparedRequest()
        req.prepare_url(endpoint, values)
        url = req.url
    else:
        url = _func(
            endpoint,
            _anchor=_anchor,
            _method=_method,
            _scheme=_scheme,
            _external=_external,
            **values,
        )
    if url is None:
        raise ValueError
    return url


def url_for(
    endpoint: str,
    _anchor: str | None = None,
    _method: str | None = None,
    _scheme: str | None = None,
    _external: bool | None = None,
    **values: Any,
) -> str:
    if _scheme is not None:
        scheme = _scheme
    else:
        scheme = config.URL_SCHEME
    return _url_for(
        endpoint,
        _anchor=_anchor,
        _method=_method,
        _scheme=scheme,
        _external=_external,
        **values,
    )


def redirect_with_query(new_url: str, code: int = 302) -> Response:
    new_parsed = urlparse(new_url)
    new_params = dict(parse_qsl(new_parsed.query))
    in_params = dict(parse_qsl(request.query_string.decode()))
    params = {**new_params, **in_params}
    query = urlencode(params, doseq=True)
    url = urlunparse(new_parsed._replace(query=query))
    return redirect(url, code=code)
