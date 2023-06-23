import bleach

_allowed_tags = {
    "a",
    "b",
    "em",
    "h3",
    "h4",
    "h5",
    "h6",
    "html",
    "i",
    "li",
    "ol",
    "p",
    "strong",
    "sub",
    "sup",
    "ul",
}
_allowed_attrs = {
    "a": ["href", "title", "target"],
}


def clean_html(html: str) -> str:
    html = html.replace("<h1>", "<h3>").replace("</h1>", "</h3>")
    html = html.replace("<h2>", "<h3>").replace("</h2>", "</h3>")
    return bleach.clean(
        html,
        tags=_allowed_tags,
        attributes=_allowed_attrs,
        strip=True,
        strip_comments=True,
    )
