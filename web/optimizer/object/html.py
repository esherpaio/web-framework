import re


def minify_html(value: str) -> str:
    # Remove non-conditional comments
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    # Remove extra spaces between tags
    value = re.sub(r">\s+<", "><", value)
    # Remove all newlines and extra spaces
    value = re.sub(r"\s+", " ", value).strip()
    return value
