import uuid

from flask_login import current_user
from sqlalchemy.orm import Session

from web.database.model import Access


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
