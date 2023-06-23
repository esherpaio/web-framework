from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import User


def get_resource(user_id: int) -> dict:
    with conn.begin() as s:
        user = s.query(User).filter_by(id=user_id).first()
        return _build(s, user)


def _build(s: Session, user: User) -> dict:
    return {
        "billing_id": user.billing_id,
        "email": user.email,
        "id": user.id,
        "is_active": user.is_active,
        "role": user.role_id,
        "shipping_id": user.shipping_id,
    }
