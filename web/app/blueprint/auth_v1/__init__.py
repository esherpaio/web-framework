from ._bp import auth_v1_bp, auth_v1_static_jobs
from .routes import login, password, register

__all__ = [
    "auth_v1_bp",
    "auth_v1_static_jobs",
    "login",
    "password",
    "register",
]
