from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.database import conn
from web.database.model import AppSettings


@admin_v1_bp.get("/admin/settings")
def settings() -> str:
    with conn.begin() as s:
        settings_ = s.query(AppSettings).first()

    return render_template(
        "admin/settings.html",
        active_menu="settings",
        settings=settings_,
    )
