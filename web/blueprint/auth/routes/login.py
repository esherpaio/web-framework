from flask import render_template

from web.app.blueprint.auth import auth_bp
from web.app.gtag import EventByClass, EventTrigger, GtagLogin


@auth_bp.get("/login")
@auth_bp.get("/<string:_locale>/login")
def login(_locale: str) -> str:
    gtags = [GtagLogin(EventByClass(EventTrigger.ON_SUBMIT))]
    return render_template("auth/login.html", gtags=gtags)
