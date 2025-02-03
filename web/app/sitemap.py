from xml.dom import minidom
from xml.dom.minidom import Node

from web.app.urls import url_for

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
    def __init__(self, endpoint: str, **kwargs) -> None:
        self._endpoint = endpoint
        self._kwargs = kwargs

    @property
    def loc(self) -> str:
        return url_for(self._endpoint, **self._kwargs, _external=True)


#
# Functions
#


def text_to_xml(value: str) -> bytes:
    def strip_node(node_: Node) -> None:
        for x in node_.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                strip_node(x)

    # Parse to DOM object
    node = minidom.parseString(value)
    # Remove empty XML elements
    strip_node(node)
    # Make pretty
    node.normalize()
    xml = node.toprettyxml(indent="  ", encoding="UTF-8")
    return xml
