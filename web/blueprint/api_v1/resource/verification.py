from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import Verification


def get_resource(verification_id: int) -> dict:
    with conn.begin() as s:
        verification = s.query(Verification).filter_by(id=verification_id).first()
        return _build(s, verification)


def _build(s: Session, verification: Verification) -> dict:
    return {
        "id": verification.id,
        "key": verification.key,
        "user_id": verification.user_id,
    }
