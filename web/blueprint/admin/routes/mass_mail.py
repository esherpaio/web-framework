from flask import render_template

from web.blueprint.admin import admin_bp


@admin_bp.get("/admin/mass-mail")
def mass_mail() -> str:
    return render_template("admin/mass_mail.html")
