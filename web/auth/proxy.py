from typing import Any

from flask import g
from sqlalchemy.orm import joinedload
from werkzeug.local import LocalProxy

from web.config import config
from web.database import conn
from web.database.model import User, UserRoleId
from web.libs.logger import log

from .enum import AuthType, G


def _get_proxy_user() -> User | None:
    # Get the user from the g object
    user = g.get(G.USER, None)
    if user is not None:
        if not getattr(g, G.USER_STORED, False):
            log.debug(f"Loaded user {user.id} from g object")
            g._user_stored = True
        return g._user

    # Load the user from the database
    user_id = g.get(G.USER_ID, None)
    if user is None and user_id is not None:
        with conn.begin() as s:
            user = (
                s.query(User)
                .options(joinedload(User.role))
                .filter_by(id=g._user_id, is_active=True)
                .first()
            )
        if user is not None:
            log.debug(f"Loaded user {user.id} from database")
            g._user = user
            return user

    # Insert a new guest user
    auth_type = g.get(G.AUTH_TYPE, None)
    if (
        config.AUTH_JWT_ALLOW_GUEST
        and user is None
        and auth_type in [AuthType.NONE, AuthType.JWT]
    ):
        with conn.begin() as s:
            user = User(is_active=True, role_id=UserRoleId.GUEST)
            s.add(user)
        log.debug(f"Inserted user {user.id} into database")
        g._user = None
        g._user_id = user.id
        g._auth_type = AuthType.JWT
        return _get_proxy_user()

    return None


current_user: Any = LocalProxy(lambda: _get_proxy_user())
