from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import Shipping


def get_resource(shipping_id: int) -> dict:
    with Conn.begin() as s:
        shipping = s.query(Shipping).filter_by(id=shipping_id).first()
        return _build(s, shipping)


def _build(s: Session, shipping: Shipping) -> dict:
    return {
        "address": shipping.address,
        "city": shipping.city,
        "company": shipping.company,
        "country_id": shipping.country_id,
        "email": shipping.email,
        "first_name": shipping.first_name,
        "id": shipping.id,
        "last_name": shipping.last_name,
        "phone": shipping.phone,
        "zip_code": shipping.zip_code,
    }
