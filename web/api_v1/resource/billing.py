from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import Billing


def get_resource(billing_id: int) -> dict:
    with conn.begin() as s:
        billing = s.query(Billing).filter_by(id=billing_id).first()
        return _build(s, billing)


def _build(s: Session, billing: Billing) -> dict:
    return {
        "id": billing.id,
    }
