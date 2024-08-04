import re
import urllib.parse
from typing import Any, Callable
from xml.dom import minidom
from xml.dom.minidom import Node

from phonenumbers.phonenumberutil import _is_viable_phone_number
from requests.models import PreparedRequest

#
# Parsing
#


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


#
# Validation
#


def is_email(text: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


def is_phone(text: str) -> bool:
    return _is_viable_phone_number(text)


def gen_slug(name: str) -> str:
    return re.sub(r"[ _]+", "-", re.sub(r"[^\w -]+", "", name)).lower()


def strip_scheme(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    scheme = f"{parsed.scheme}://"
    return parsed.geturl().replace(scheme, "", 1)


#
# Conversion
#


def str_to_xml(string: str) -> bytes:
    def strip_node(node_: Node) -> None:
        for x in node_.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                strip_node(x)

    # Parse to DOM object
    node = minidom.parseString(string)
    # Remove empty XML elements
    strip_node(node)
    # Make pretty
    node.normalize()
    xml = node.toprettyxml(indent="  ", encoding="UTF-8")
    return xml
