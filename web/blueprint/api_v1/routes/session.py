import time
from enum import StrEnum
from random import randint

import flask_login
from werkzeug import Response
from werkzeug.security import check_password_hash

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import User
from web.helper.api import json_get, response
from web.helper.cart import transfer_cart
from web.i18n.base import _

#
# Configuration
#


class Text(StrEnum):
    CHECK_DETAILS = _("API_SESSION_CHECK_DETAILS")
    CHECK_ACTIVATION = _("API_SESSION_CHECK_ACTIVATION")


#
# Endpoints
#


@api_v1_bp.post("/sessions")
@transfer_cart
def post_session() -> Response:
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


@api_v1_bp.delete("/sessions")
def delete_session() -> Response:
    # Wait random interval
    sleep_s = randint(0, 1000) / 1000
    time.sleep(sleep_s)

    # Logout user
    flask_login.logout_user()
    return response()


#
# Functions
#
