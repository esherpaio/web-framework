import time
from enum import StrEnum
from random import randint

import flask_login
from flask import Response
from werkzeug.security import check_password_hash

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import User
from web.helper.api import json_get, response
from web.helper.cart import transfer_cart
from web.helper.user import FlaskUser
from web.i18n.base import _


class _Text(StrEnum):
    CHECK_DETAILS = _("API_SESSION_CHECK_DETAILS")
    CHECK_ACTIVATION = _("API_SESSION_CHECK_ACTIVATION")


@api_v1_bp.post("/sessions")
@transfer_cart
def post_session() -> Response:
    email, _ = json_get("email", str, nullable=False, lower_str=True)
    password, _ = json_get("password", str, nullable=False)

    # Get user
    with conn.begin() as s:
        user = s.query(User).filter_by(email=email).first()

    # Check if user exists
    if not user:
        return response(400, _Text.CHECK_DETAILS)
    # Check if user activation is pending
    if not user.is_active:
        return response(400, _Text.CHECK_ACTIVATION)
    # Check if password is correct
    if not check_password_hash(user.password_hash, password):
        return response(400, _Text.CHECK_DETAILS)

    # Wait random interval
    sleep_s = randint(0, 2000) / 1000
    time.sleep(sleep_s)

    # Login user
    flask_user = FlaskUser(user)
    flask_login.login_user(flask_user, remember=True)

    return response()


@api_v1_bp.delete("/sessions")
def delete_session() -> Response:
    # Wait random interval
    sleep_s = randint(0, 2000) / 1000
    time.sleep(sleep_s)

    # Logout user
    flask_login.logout_user()

    return response()
