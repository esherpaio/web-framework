from flask import Response

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import ShipmentClass, ShipmentMethod, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/shipment-classes")
def post_shipment_classes() -> Response:
    name, _ = json_get("name", str, nullable=False)
    order, _ = json_get("order", int, nullable=False)

    with conn.begin() as s:
        # Raise if shipment_class exists
        shipment_class = (
            s.query(ShipmentClass).filter_by(name=name, is_deleted=False).first()
        )
        if shipment_class:
            return response(409, ApiText.HTTP_409)

        # Insert shipment_class
        shipment_class = ShipmentClass(name=name, order=order)
        s.add(shipment_class)

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/shipment-classes/<int:shipment_class_id>")
def patch_shipment_classes_id(shipment_class_id: int) -> Response:
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get shipment_zone
        # Raise if shipment_zone doesn't exist
        shipment_zone = s.query(ShipmentClass).filter_by(id=shipment_class_id).first()
        if not shipment_zone:
            return response(404, ApiText.HTTP_404)

        # Update order
        if has_order:
            shipment_zone.order = order

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/shipment-classes/<int:shipment_class_id>")
def delete_shipment_classes_id(shipment_class_id: int) -> Response:
    with conn.begin() as s:
        # Set shipment class to deleted
        shipment_class = s.query(ShipmentClass).filter_by(id=shipment_class_id).first()
        if not shipment_class:
            return response(404, ApiText.HTTP_404)
        shipment_class.is_deleted = True

        # Set shipment zones to deleted
        shipment_zones = (
            s.query(ShipmentMethod)
            .filter_by(class_id=shipment_class_id, is_deleted=False)
            .all()
        )
        for shipment_zone in shipment_zones:
            shipment_zone.is_deleted = True

    return response()
