import bleach

_allowed_attrs = {
    "a": ["href", "title", "target"],
}


def clean_html(html: str) -> str:
    return bleach.clean(
        html,
        attributes=_allowed_attrs,
        strip=True,
        strip_comments=True,
    )
