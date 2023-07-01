from typing import Callable

import flask_login
from flask import Response, redirect, request, url_for
from flask_login import current_user
from sqlalchemy.orm import Session, joinedload

from web import config
from web.database.client import conn
from web.database.model import User, UserRoleId, UserRoleLevel
from web.helper.api import ApiText, response


class FlaskUser(User):
    def __init__(self, user: User) -> None:
        super().__init__()
        for key, value in vars(user).items():
            if key.startswith("_"):
                continue
            setattr(self, key, value)

    @property
    def is_authenticated(self) -> bool:
        return not self.is_guest

    @property
    def is_anonymous(self) -> bool:
        return self.is_guest

    def get_id(self) -> int:
        return self.id


def load_user(user_id: int, *args, **kwargs) -> FlaskUser | None:
    with conn.begin() as s:
        user = (
            s.query(User)
            .options(joinedload(User.role))
            .filter_by(id=user_id, is_active=True)
            .first()
        )
    if user is not None:
        return FlaskUser(user)


def load_request(*args, **kwargs) -> FlaskUser:
    with conn.begin() as s:
        user = User(is_active=True, role_id=UserRoleId.GUEST)
        s.add(user)
    flask_login.login_user(FlaskUser(user))
    return user


def access_control(
    level: UserRoleLevel,
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Authorize a user based on their role level."""

    def decorate(f: Callable) -> Callable[..., Response]:
        def wrap(*args, **kwargs) -> Response:
            if current_user.is_authenticated and current_user.role.level >= level:
                return f(*args, **kwargs)
            elif "api" in request.blueprint:
                return response(403, ApiText.HTTP_403)
            else:
                return redirect(url_for(config.ENDPOINT_LOGIN))

        wrap.__name__ = f.__name__
        return wrap

    return decorate
