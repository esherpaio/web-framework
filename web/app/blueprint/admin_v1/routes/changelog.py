import os

from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.config import config


@admin_v1_bp.get("/admin/changelog")
def changelog() -> str:
    fp = os.path.join(config.APP_ROOT, "RELEASE.md")
    with open(fp, "r") as file_:
        data = file_.read()
    return render_template(
        "admin/changelog.html",
        changelog=data,
    )
