def minify_html(value: str) -> str:
    lines = []
    for line in value.splitlines():
        strip = line.strip()
        if strip:
            lines.append(strip)
    return "\n".join(lines)
