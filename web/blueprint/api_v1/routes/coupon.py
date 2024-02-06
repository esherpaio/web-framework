from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Coupon, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/coupons")
@access_control(UserRoleLevel.ADMIN)
def post_coupons() -> Response:
    amount, _ = json_get("amount", int | float)
    code, _ = json_get("code", str, nullable=False)
    percentage, _ = json_get("percentage", int)
    rate = abs(percentage / 100 - 1) if percentage else None

    with conn.begin() as s:
        # Check if coupon already exists
        coupon = s.query(Coupon).filter_by(code=code, is_deleted=False).first()
        if coupon:
            return response(409, ApiText.HTTP_409)

        # Insert coupon
        coupon = Coupon(code=code, rate=rate, amount=amount)
        s.add(coupon)

    return response()


@api_v1_bp.delete("/coupons/<int:coupon_id>")
@access_control(UserRoleLevel.ADMIN)
def delete_coupons_id(coupon_id: int) -> Response:
    with conn.begin() as s:
        # Delete coupon
        coupon = s.query(Coupon).filter_by(id=coupon_id).first()
        if not coupon:
            return response(404, ApiText.HTTP_404)
        coupon.is_deleted = True

    return response()


#
# Functions
#
