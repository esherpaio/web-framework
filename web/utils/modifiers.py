import urllib.parse
from xml.dom import minidom
from xml.dom.minidom import Node


def strip_scheme(url: str) -> str:
    url_parsed = urllib.parse.urlparse(url)
    scheme = f"{url_parsed.scheme}://"
    return url_parsed.geturl().replace(scheme, "", 1)


def replace_domain(in_url: str, new_domain: str) -> str:
    new_domain = strip_scheme(new_domain)
    in_url_parsed = urllib.parse.urlparse(in_url)
    new_url_parsed = in_url_parsed._replace(netloc=new_domain)
    return urllib.parse.urlunparse(new_url_parsed)


def text_to_xml(value: str) -> bytes:
    def strip_node(node_: Node) -> None:
        for x in node_.childNodes:
            if x.nodeType == Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == Node.ELEMENT_NODE:
                strip_node(x)

    node = minidom.parseString(value)
    strip_node(node)
    node.normalize()
    xml = node.toprettyxml(indent="  ", encoding="UTF-8")
    return xml
