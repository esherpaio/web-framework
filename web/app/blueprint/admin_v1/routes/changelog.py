import os

from flask import render_template
from markupsafe import Markup

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.config import config


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
            if is_indent:
                indent_count = max(len(line) - len(line.lstrip(" ")), 1)
            else:
                indent_count = 0
            indent_text = line.strip(" -")
            if indent_count > indent_level:
                data.append("<ul>")
            elif indent_count < indent_level:
                data.append("</ul>")
            indent_level = indent_count

            if is_heading:
                data.append(f"<h{heading_level}>{heading_text}</h{heading_level}>")
            if is_indent:
                data.append(f"<li>{indent_text}</li>")

        return Markup("".join(data))


@admin_v1_bp.get("/admin/changelog")
def changelog() -> str:
    fp = os.path.join(config.APP_ROOT, "RELEASE.md")
    with open(fp, "r") as file_:
        lines = file_.readlines()
    changelog_html = Markdown(*lines).html
    return render_template("admin/changelog.html", changelog_html=changelog_html)
