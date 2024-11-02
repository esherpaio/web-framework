from flask import render_template

from web.blueprint.auth import auth_bp


@auth_bp.get("/password-request")
@auth_bp.get("/<string:_locale>/password-request")
def password_request(_locale: str) -> str:
    return render_template("auth/password_request.html")


@auth_bp.get("/password-recover")
@auth_bp.get("/<string:_locale>/password-recover")
def password_recover(_locale: str) -> str:
    return render_template("auth/password_recover.html")
