from flask import render_template

from web.app.blueprint import admin_bp


@admin_bp.get("/admin/changelog")
def changelog() -> str:
    return render_template(
        "admin/changelog.html",
        changelog=changelog,
    )
