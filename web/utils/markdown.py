from markupsafe import Markup


class Markdown:
    def __init__(self, *lines: str) -> None:
        self._lines = lines

    @property
    def html(self) -> str:
        data = []
        indent_level = 0

        for line in self._lines:
            strip_space = line.strip(" ")

            is_heading = strip_space.startswith("#")
            heading_level = line.count("#") + 1
            heading_text = line.strip(" #")
            is_indent = strip_space.startswith("-")
            indent_text = line.strip(" -")

            if is_indent:
                indent_count = max(len(line) - len(line.lstrip(" ")), 1)
            else:
                indent_count = 0

            while indent_count > indent_level:
                data.append("<ul>")
                indent_level += 1
            while indent_count < indent_level:
                data.append("</ul>")
                indent_level -= 1

            if is_heading:
                data.append(f"<h{heading_level}>{heading_text}</h{heading_level}>")
            if is_indent:
                data.append(f"<li>{indent_text}</li>")

        return Markup("".join(data))
