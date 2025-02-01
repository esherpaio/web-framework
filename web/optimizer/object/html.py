import re

import rjsmin


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

    # Split HTML and isolate script blocks
    parts = re.split(r"(<script[\s\S]*?</script>)", value, flags=re.IGNORECASE)
    for i, part in enumerate(parts):
        # Remove all newlines and extra spaces
        if not re.match(r"^\s*<script", part, flags=re.IGNORECASE):
            parts[i] = re.sub(r"\s+", " ", part).strip()

    # Join and remove new lines
    final = "".join(parts)
    final = re.sub(r"\s*\n\s*", " ", final).strip()
    return final
