from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.database import conn
from web.database.model import Country


@admin_v1_bp.get("/admin/countries")
def countries() -> str:
    with conn.begin() as s:
        countries = s.query(Country).order_by(Country.name).all()
    return render_template(
        "admin/countries.html",
        countries=countries,
    )
