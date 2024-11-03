from flask import render_template

from web.app.blueprint.auth_v1 import auth_v1_bp


@auth_v1_bp.get("/password-request")
@auth_v1_bp.get("/<string:_locale>/password-request")
def password_request(_locale: str) -> str:
    return render_template("auth/password_request.html")


@auth_v1_bp.get("/password-recover")
@auth_v1_bp.get("/<string:_locale>/password-recover")
def password_recover(_locale: str) -> str:
    return render_template("auth/password_recover.html")
