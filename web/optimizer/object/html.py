import re


def minify_html(value: str) -> str:
    # Remove non-conditional comments
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    # Remove extra spaces between tags
    value = re.sub(r">\s+<", "><", value)
    # Remove empty lines
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return "\n".join(lines)
