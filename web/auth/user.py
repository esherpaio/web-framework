from typing import Any

from flask import g, has_request_context
from sqlalchemy.orm import joinedload
from werkzeug.local import LocalProxy

from web.database import conn
from web.database.model import User

from .enum import AuthType, G


def _get_proxy_user() -> User | None:
    if has_request_context():
        if G.USER in g:
            return g._user
        if G.USER not in g and G.USER_ID in g:
            with conn.begin() as s:
                user = (
                    s.query(User)
                    .options(joinedload(User.role))
                    .filter_by(id=g._user_id, is_active=True)
                    .first()
                )
            if user is not None:
                g._user = user
                return user
            else:
                g._user = None
                g._user_id = None
                g._user_auth = AuthType.NONE
    return None


current_user: Any = LocalProxy(lambda: _get_proxy_user())
