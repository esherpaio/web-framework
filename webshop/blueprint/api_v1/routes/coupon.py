from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.database.client import Conn
from webshop.database.model import Coupon
from webshop.database.model.user_role import UserRoleLevel
from webshop.helper.api import json_get, response, ApiText
from webshop.helper.security import authorize


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/coupons")
def post_coupons() -> Response:
    amount, _ = json_get("amount", int | float)
    code, _ = json_get("code", str, nullable=False)
    percentage, _ = json_get("percentage", int)
    rate = abs(percentage / 100 - 1) if percentage else None

    with Conn.begin() as s:
        # Raise if coupon exists
        coupon = s.query(Coupon).filter_by(code=code, is_deleted=False).first()
        if coupon:
            return response(409, ApiText.HTTP_409)

        # Add coupon
        coupon = Coupon(code=code, rate=rate, amount=amount)
        s.add(coupon)

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/coupons/<int:coupon_id>")
def delete_coupons_id(coupon_id: int) -> Response:
    with Conn.begin() as s:
        # Get coupon
        # Raise if coupon doesn't exist
        coupon = s.query(Coupon).filter_by(id=coupon_id).first()
        if not coupon:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        coupon.is_deleted = True

    return response()
