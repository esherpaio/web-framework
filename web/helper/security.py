import uuid
from typing import Callable

from flask import Response, redirect, request, url_for
from flask_login import current_user
from sqlalchemy.orm import Session

from web import config
from web.database.model import Access, UserRoleLevel
from web.helper.api import ApiText, response


def get_access(s: Session) -> Access:
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


def authorize(
    level: UserRoleLevel,
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
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
