from flask import render_template
from sqlalchemy.orm import joinedload

from web.app.blueprint.admin import admin_bp
from web.database import conn
from web.database.model import ShipmentZone


@admin_bp.get("/admin/shipment-zones")
def shipment_zones() -> str:
    with conn.begin() as s:
        shipment_zones_ = (
            s.query(ShipmentZone)
            .options(
                joinedload(ShipmentZone.country),
                joinedload(ShipmentZone.region),
            )
            .filter_by(is_deleted=False)
            .order_by(ShipmentZone.order, ShipmentZone.id)
            .all()
        )

    return render_template(
        "admin/shipment_zones.html",
        shipment_zones=shipment_zones_,
    )
