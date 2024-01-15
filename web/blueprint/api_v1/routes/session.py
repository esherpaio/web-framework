import time
from enum import StrEnum
from random import randint

import flask_login
from google.auth.transport import requests
from google.oauth2 import id_token
from werkzeug import Response
from werkzeug.security import check_password_hash

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import User, UserRoleId
from web.helper.api import json_get, response
from web.helper.cart import transfer_cart
from web.i18n.base import _

#
# Configuration
#


class Text(StrEnum):
    CHECK_DETAILS = _("API_SESSION_CHECK_DETAILS")
    CHECK_ACTIVATION = _("API_SESSION_CHECK_ACTIVATION")
    GOOGLE_INVALID = _("API_SESSION_GOOGLE_INVALID")


#
# Endpoints
#


@api_v1_bp.post("/sessions")
@transfer_cart
def post_sessions() -> Response:
    email, _ = json_get("email", str, nullable=False)
    password, _ = json_get("password", str, nullable=False)
    remember, _ = json_get("remember", bool, default=False)

    # Get user
    with conn.begin() as s:
        user = s.query(User).filter_by(email=email.lower()).first()

    # Validate user
    if not user:
        return response(400, Text.CHECK_DETAILS)
    if not user.is_active:
        return response(400, Text.CHECK_ACTIVATION)
    if not check_password_hash(user.password_hash, password):
        return response(400, Text.CHECK_DETAILS)

    # Wait random interval
    sleep_s = randint(0, 1000) / 1000
    time.sleep(sleep_s)

    # Login user
    flask_login.login_user(user, remember=remember)
    return response()


@api_v1_bp.post("/sessions/google")
@transfer_cart
def post_sessions_google() -> Response:
    token_id, _ = json_get("token_id", str, nullable=False)
    token = id_token.verify_oauth2_token(
        token_id, requests.Request(), audience=config.GOOGLE_CLIENT_ID
    )
    email = token.get("email")
    if email is None:
        return response(400, Text.GOOGLE_INVALID)
    email = email.lower()

    # Get or add user
    with conn.begin() as s:
        user = s.query(User).filter_by(email=email, is_active=True).first()
    if user and not user.is_active:
        return response(400, Text.CHECK_ACTIVATION)
    if not user:
        with conn.begin() as s:
            user = User(email=email, is_active=True, role_id=UserRoleId.USER)
            s.add(user)

    # Login user
    flask_login.login_user(user, remember=False)
    return response()


@api_v1_bp.delete("/sessions")
def delete_sessions() -> Response:
    # Wait random interval
    sleep_s = randint(0, 1000) / 1000
    time.sleep(sleep_s)

    # Logout user
    flask_login.logout_user()
    return response()


#
# Functions
#
