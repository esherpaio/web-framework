import re
import urllib.parse
from xml.dom import minidom
from xml.dom.minidom import Node

#
# Validation
#


def is_email(text: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))


def is_phone(text: str) -> bool:
    return bool(re.match(r"(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text))


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
    """Convert a string to an XML object."""

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
