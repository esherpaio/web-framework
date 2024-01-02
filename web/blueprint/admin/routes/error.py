from flask import render_template

from web.blueprint.admin import admin_bp


@admin_bp.get("/admin/error")
def error() -> str:
    return render_template("admin/error.html")
