from ._bp import auth_bp, js_bundle_login, js_bundle_password, js_bundle_register
from .routes import login, password, register

__all__ = [
    "auth_bp",
    "js_bundle_login",
    "js_bundle_password",
    "js_bundle_register",
    "login",
    "password",
    "register",
]
