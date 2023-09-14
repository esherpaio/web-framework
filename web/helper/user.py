import base64
from typing import Callable

import flask_login
from flask import abort, redirect, request, url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload
from werkzeug import Response

from web import config
from web.database.client import conn
from web.database.model import User, UserRoleId, UserRoleLevel
from web.helper.api import ApiText, response

#
# Functions
#


def cookie_loader(user_id: int, *args, **kwargs) -> User | None:
    return _get_user_session(user_id)


def session_loader(*args, **kwargs) -> User | None:
    if request.blueprint is not None and "api" in request.blueprint:
        user = _get_api_session()
        if user is None:
            user = _set_guest_session(persistent=True)
    else:
        user = _set_guest_session()
    return user


def _get_api_session() -> User | None:
    authorization = request.headers.get("Authorization")
    if authorization is not None:
        encoded = authorization.replace("Basic ", "", 1).encode()
        api_key = base64.b64decode(encoded).decode()
        with conn.begin() as s:
            user = (
                s.query(User)
                .options(joinedload(User.role))
                .filter_by(api_key=api_key, is_active=True)
                .first()
            )
        if user is not None:
            return user
        abort(response(401, ApiText.HTTP_401))


def _get_user_session(user_id: int) -> User | None:
    with conn.begin() as s:
        user = (
            s.query(User)
            .options(joinedload(User.role))
            .filter_by(id=user_id, is_active=True)
            .first()
        )
    if user is not None:
        return user


def _set_guest_session(persistent: bool = False) -> User:
    if persistent:
        with conn.begin() as s:
            user = User(is_active=True, role_id=UserRoleId.GUEST)
            s.add(user)
        flask_login.login_user(user)
    else:
        user = User()
    return user


#
# Decorators
#


def access_control(
    level: UserRoleLevel,
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Authorize a user based on their role level."""

    def decorate(f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            if current_user.is_authenticated and current_user.role.level >= level:
                return f(*args, **kwargs)
            if request.blueprint is not None and "api" in request.blueprint:
                return response(403, ApiText.HTTP_403)
            return redirect(url_for(config.ENDPOINT_LOGIN))

        wrap.__name__ = f.__name__
        return wrap

    return decorate
