import re


def minify_html(value: str) -> str:
    # strip comments
    html = re.sub("(<!--.*?-->)", "", value, flags=re.DOTALL)
    # strip empty lines
    html = "\n".join(filter(str.strip, value.splitlines()))
    return html
