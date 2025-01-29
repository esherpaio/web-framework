import os

from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.app.blueprint.admin_v1._utils import Markdown
from web.config import config


@admin_v1_bp.get("/admin/changelog")
def changelog() -> str:
    changelog_fp = os.path.join(config.APP_ROOT, "RELEASE.md")
    with open(changelog_fp, "r") as file_:
        changelog_lines = file_.readlines()
    changelog_html = Markdown(*changelog_lines).html
    return render_template(
        "admin/changelog.html",
        active_menu="changelog",
        changelog_html=changelog_html,
    )
