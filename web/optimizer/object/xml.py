import re


_MARKUP_PATTERN = re.compile(
    r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<(?:\"[^\"]*\"|'[^']*'|[^'\">])*>",
    re.DOTALL,
)


def _collapse_markup_whitespace(markup: str) -> str:
    if markup.startswith(("<!--", "<![CDATA[")):
        return markup

    result: list[str] = []
    quote: str | None = None
    whitespace_pending = False

    for character in markup:
        if quote is not None:
            result.append(character)
            if character == quote:
                quote = None
            continue

        if character in {'"', "'"}:
            if whitespace_pending:
                result.append(" ")
                whitespace_pending = False
            result.append(character)
            quote = character
        elif character.isspace():
            whitespace_pending = True
        else:
            if whitespace_pending and character != ">" and result[-1] != "<":
                result.append(" ")
            whitespace_pending = False
            result.append(character)

    return "".join(result)


def minify_xml(value: str) -> str:
    result: list[str] = []
    position = 0

    for match in _MARKUP_PATTERN.finditer(value):
        text = value[position : match.start()]
        if text.strip():
            result.append(text)
        result.append(_collapse_markup_whitespace(match.group()))
        position = match.end()

    text = value[position:]
    if text.strip():
        result.append(text)

    return "".join(result)
