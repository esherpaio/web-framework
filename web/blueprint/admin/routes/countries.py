from flask import render_template

from web.blueprint.admin import admin_bp
from web.database.client import conn
from web.database.model import Country


@admin_bp.get("/admin/countries")
def countries() -> str:
    with conn.begin() as s:
        countries = s.query(Country).order_by(Country.name).all()
    return render_template(
        "admin/countries.html",
        countries=countries,
    )
