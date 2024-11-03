from ._bp import auth_v1_bp, auth_v1_js_login, auth_v1_js_password, auth_v1_js_register
from .routes import login, password, register

__all__ = [
    "auth_v1_bp",
    "auth_v1_js_login",
    "auth_v1_js_password",
    "auth_v1_js_register",
    "login",
    "password",
    "register",
]
