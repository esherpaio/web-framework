from flask import render_template

from web.app.blueprint.auth_v1 import auth_v1_bp
from web.app.gtag import EventByClass, EventTrigger, Gtags, GtagSignUp


@auth_v1_bp.get("/register")
@auth_v1_bp.get("/<string:_locale>/register")
def register(_locale: str) -> str:
    gtags = Gtags(GtagSignUp(EventByClass(EventTrigger.ON_SUBMIT)))
    return render_template("auth/register.html", gtags=gtags)
