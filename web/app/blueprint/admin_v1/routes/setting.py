from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.database import conn
from web.database.model import AppSetting


@admin_v1_bp.get("/admin/setting")
def setting() -> str:
    with conn.begin() as s:
        setting_ = s.query(AppSetting).first()

    return render_template(
        "admin/setting.html",
        setting=setting_,
    )
