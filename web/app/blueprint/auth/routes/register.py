from flask import render_template
from web.app.gtag import EventByClass, EventTrigger, GtagSignUp

from web.app.blueprint.auth import auth_bp


@auth_bp.get("/register")
@auth_bp.get("/<string:_locale>/register")
def register(_locale: str) -> str:
    gtags = [GtagSignUp(EventByClass(EventTrigger.ON_SUBMIT))]
    return render_template("auth/register.html", gtags=gtags)
