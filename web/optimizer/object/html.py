import re

import rjsmin

PRESERVE_RE = re.compile(
    r"<(script|textarea|pre)\b[^>]*>[\s\S]*?</\1\s*>",
    flags=re.IGNORECASE,
)


def minify_html(value: str) -> str:
    # Remove comments
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)

    def minify_script(match: re.Match) -> str:
        tag_open = re.sub(r"\s+", " ", match.group(1)).strip()
        content = match.group(2)
        tag_close = re.sub(r"\s+", " ", match.group(3)).strip()
        minified = rjsmin.jsmin(content, keep_bang_comments=False)
        return f"{tag_open}{minified}{tag_close}"

    # Minify script blocks
    value = re.sub(
        r"(?i)(<script[^>]*>)([\s\S]*?)(</script>)",
        minify_script,
        value,
    )

    parts = []
    index = 0
    for match in PRESERVE_RE.finditer(value):
        parts.append(re.sub(r"\s+", " ", value[index : match.start()]))
        parts.append(match.group(0))
        index = match.end()
    parts.append(re.sub(r"\s+", " ", value[index:]))

    return "".join(parts).strip()
