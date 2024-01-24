from flask import render_template

from web.blueprint.admin import admin_bp
from web.database.client import conn
from web.database.model import AppSetting


@admin_bp.get("/admin/setting")
def setting() -> str:
    with conn.begin() as s:
        setting_ = s.query(AppSetting).first()

    return render_template(
        "admin/setting.html",
        setting=setting_,
    )
