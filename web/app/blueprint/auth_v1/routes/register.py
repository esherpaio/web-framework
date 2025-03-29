from flask import render_template

from web.app.blueprint.auth_v1 import auth_v1_bp
from web.app.data_layer import ByClass, Events, EventSignUp, On


@auth_v1_bp.get("/register")
@auth_v1_bp.get("/<string:_locale>/register")
def register(_locale: str) -> str:
    events = Events(EventSignUp(ByClass(On.SUBMIT)))
    return render_template("auth/register.html", events=events)
