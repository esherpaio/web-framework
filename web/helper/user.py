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
# User object
#


class FlaskUser(User):
    def __init__(self, user: User) -> None:
        super().__init__()
        for key, value in vars(user).items():
            if key.startswith("_"):
                continue
            setattr(self, key, value)

    @property
    def is_authenticated(self) -> bool:
        return not self.is_guest and self.is_active

    @property
    def is_anonymous(self) -> bool:
        return self.is_guest

    def get_id(self) -> int:
        return self.id


#
# Cookie based authentication
#


def cookie_loader(user_id: int, *args, **kwargs) -> FlaskUser | None:
    with conn.begin() as s:
        user = (
            s.query(User)
            .options(joinedload(User.role))
            .filter_by(id=user_id, is_active=True)
            .first()
        )
    if user is not None:
        return FlaskUser(user)


#
# Session based authentication
#


def session_loader(*args, **kwargs) -> FlaskUser | None:
    user = _load_request_api()
    if user is not None:
        return user
    user = _load_request_session()
    if user is not None:
        return user


def _load_request_api() -> FlaskUser | None:
    authorization = request.headers.get("Authorization")
    if authorization is not None:
        encoded = authorization.replace("Basic ", "", 1).encode()
        api_key = base64.b64decode(encoded).decode()
        with conn.begin() as s:
            user = (
                s.query(User)
                .options(joinedload(User.role))
                .filter_by(api_key=api_key)
                .first()
            )
        if user is not None:
            return FlaskUser(user)
        abort(response(401, ApiText.HTTP_401))


def _load_request_session() -> FlaskUser | None:
    with conn.begin() as s:
        user = User(is_active=True, role_id=UserRoleId.GUEST)
        s.add(user)
    flask_user = FlaskUser(user)
    flask_login.login_user(flask_user)
    return flask_user


#
# Route decorators
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
