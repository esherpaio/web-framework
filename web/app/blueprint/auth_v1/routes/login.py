from flask import render_template

from web.app.blueprint.auth_v1 import auth_v1_bp
from web.app.gtag import EventByClass, EventTrigger, GtagLogin, Gtags


@auth_v1_bp.get("/login")
@auth_v1_bp.get("/<string:_locale>/login")
def login(_locale: str) -> str:
    gtags = Gtags(GtagLogin(EventByClass(EventTrigger.ON_SUBMIT)))
    return render_template("auth/login.html", gtags=gtags)
