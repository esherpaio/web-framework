from flask import render_template

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.database import conn
from web.database.model import ShipmentClass


@admin_v1_bp.get("/admin/shipment-classes")
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
        active_menu="shipments",
        shipment_classes=shipment_classes_,
    )
