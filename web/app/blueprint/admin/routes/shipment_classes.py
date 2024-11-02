from flask import render_template

from web.app.blueprint import admin_bp
from web.database import conn
from web.database.model import ShipmentClass


@admin_bp.get("/admin/shipment-classes")
def shipment_classes() -> str:
    with conn.begin() as s:
        shipment_classes_ = (
            s.query(ShipmentClass)
            .filter_by(is_deleted=False)
            .order_by(ShipmentClass.order, ShipmentClass.id)
            .all()
        )

    return render_template(
        "admin/shipment_classes.html",
        shipment_classes=shipment_classes_,
    )
