from flask import render_template

from web.app.blueprint.auth_v1 import auth_v1_bp
from web.app.data_layer import ByClass, EventLogin, Events, On


@auth_v1_bp.get("/login")
@auth_v1_bp.get("/<string:_locale>/login")
def login(_locale: str) -> str:
    events = Events(EventLogin(ByClass(On.SUBMIT)))
    return render_template("auth/login.html", events=events)
