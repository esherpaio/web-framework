import time
from enum import StrEnum
from random import randint

import flask_login
from flask import url_for, Response
from flask_login import current_user
from sqlalchemy import func
from werkzeug.security import check_password_hash

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn

if config.WEBSHOP_MODE:
    from web.database.model import Cart

from web.database.model import User
from web.helper.api import response, json_get
from web.helper.cart import transfer_cart, update_cart_count
from web.helper.security import get_access
from web.helper.user import KnownUser


class _Text(StrEnum):
    CHECK_DETAILS = "Please check your login details."
    CHECK_ACTIVATION = "Please activate your account."


@api_v1_bp.post("/sessions")
@transfer_cart
def post_session() -> Response:
    email, _ = json_get("email", str, nullable=False)
    password, _ = json_get("password", str, nullable=False)

    # Get user
    with conn.begin() as s:
        user = s.query(User).filter(func.lower(User.email) == func.lower(email)).first()

    # Raise if user doesn't exist
    # Raise if user not active
    # Raise if wrong password
    if not user or not user.id:
        return response(400, _Text.CHECK_DETAILS)
    if not user.is_active:
        return response(400, _Text.CHECK_ACTIVATION)
    if not check_password_hash(user.password_hash, password):
        return response(400, _Text.CHECK_DETAILS)

    # Wait random interval
    # Login user
    sleep_s = randint(0, 2000) / 1000
    time.sleep(sleep_s)
    flask_login.login_user(KnownUser(user), remember=True)

    # Create links
    if current_user.redirect:
        redirect = current_user.redirect
    else:
        redirect = url_for(config.ENDPOINT_USER)
    current_user.redirect = None
    links = {"redirect": redirect}

    return response(links=links)


@api_v1_bp.delete("/sessions")
def delete_session() -> Response:
    # Logout user
    flask_login.logout_user()

    # Update cart_count
    if config.WEBSHOP_MODE:
        with conn.begin() as s:
            access = get_access(s)
            cart = s.query(Cart).filter_by(access_id=access.id).first()
            update_cart_count(s, cart)

    links = {"redirect": url_for(config.ENDPOINT_HOME, _locale=current_user.locale)}
    return response(links=links)
