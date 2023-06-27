import uuid
from enum import StrEnum
from typing import Callable

from flask import Response, redirect, request, session, url_for
from flask_login import AnonymousUserMixin, current_user
from sqlalchemy.orm import Session, joinedload

from web import config
from web.database.client import conn
from web.database.model import Access, User, UserRoleLevel
from web.helper.api import ApiText, response


class Session(StrEnum):
    KEY = "key"


class UserAttrs:
    @property
    def key(self) -> str | None:
        return session.get(Session.KEY)

    @key.setter
    def key(self, value: str | None) -> None:
        session[Session.KEY] = value


class KnownUser(User, UserAttrs):
    def __init__(self, user: User) -> None:
        super().__init__()

        for key, value in vars(user).items():
            if key.startswith("_"):
                continue
            setattr(self, key, value)

        if not hasattr(self, "is_active"):
            self.is_active = False

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> int:
        return self.id


class GuestUser(AnonymousUserMixin, UserAttrs):
    pass


def load_user(user_id: int) -> KnownUser | None:
    with conn.begin() as s:
        user = (
            s.query(User)
            .options(joinedload(User.role))
            .filter_by(id=user_id, is_active=True)
            .first()
        )
    if user is not None:
        return KnownUser(user)


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


def get_access(s: Session) -> Access:
    """Get an access object for the current user."""

    user_id = current_user.get_id()
    user_key = current_user.key
    if not user_key:
        user_key = str(uuid.uuid4())
        current_user.key = user_key

    if user_id:
        kwargs = {"user_id": user_id}
    else:
        kwargs = {"session_key": user_key}

    access = s.query(Access).filter_by(**kwargs).first()
    if not access:
        access = Access(**kwargs)
        s.add(access)
        s.flush()

    return access
