from datetime import datetime
from typing import Any
from xml.dom import minidom
from xml.dom.minidom import Node

from flask import current_app, request, url_for
from werkzeug.local import LocalProxy

from web.database.model import Page
from web.helper.cache import cache

#
# Classes
#


class Sitemap:
    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint

    @property
    def loc(self) -> str:
        return url_for(self._endpoint, _external=True)


class SitemapUrl:
    def __init__(
        self, endpoint: str, updated_at: datetime | None = None, **kwargs
    ) -> None:
        self._endpoint = endpoint
        self._updated_at = updated_at
        self._kwargs = kwargs

    @property
    def loc(self) -> str:
        return url_for(self._endpoint, **self._kwargs, _scheme="https", _external=True)

    @property
    def lastmod(self) -> str | None:
        if self._updated_at:
            return self._updated_at.strftime("%Y-%m-%d")


#
# Functions
#


def str_to_xml(string: str) -> bytes:
    """Convert a string to an XML object."""

    def _remove_blanks(node_: Node) -> None:
        for x in node_.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                _remove_blanks(x)

    # Parse to DOM object
    node = minidom.parseString(string)
    # Remove empty XML elements
    _remove_blanks(node)
    # Make pretty
    node.normalize()
    xml = node.toprettyxml(indent="  ", encoding="UTF-8")
    return xml


def is_endpoint(endpoint: str) -> bool:
    """Check if an endpoint exists."""
    try:
        current_app.url_map.iter_rules(endpoint)
    except KeyError:
        return False
    else:
        return True


def get_page(pages: list[Page]) -> Page | None:
    """Get a page object for the current request."""
    for page in pages:
        if page.endpoint == request.endpoint:
            return page


def _get_page() -> Page | None:
    """Get a page object for the current request."""
    for page in cache.pages:
        if page.endpoint == request.endpoint:
            return page


#
# Variables
#

current_page: Any = LocalProxy(lambda: _get_page())
