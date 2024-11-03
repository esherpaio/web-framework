from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp


@admin_v1_bp.get("/admin/changelog")
def changelog() -> str:
    return render_template(
        "admin/changelog.html",
        changelog=changelog,
    )
