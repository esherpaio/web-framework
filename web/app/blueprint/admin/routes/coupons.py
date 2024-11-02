from flask import render_template

from web.blueprint.admin import admin_bp
from web.database import conn
from web.database.model import Coupon


@admin_bp.get("/admin/coupons")
def coupons() -> str:
    with conn.begin() as s:
        coupons_ = (
            s.query(Coupon)
            .filter_by(is_deleted=False)
            .order_by(Coupon.code, Coupon.id)
            .all()
        )

    return render_template(
        "admin/coupons.html",
        coupons=coupons_,
    )
