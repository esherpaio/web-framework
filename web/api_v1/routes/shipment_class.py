from flask import Response

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import ShipmentClass, UserRoleLevel
from web.helper.api import ApiText, authorize, json_get, response


@authorize(UserRoleLevel.ADMIN)
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


@authorize(UserRoleLevel.ADMIN)
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
            shipment_zone.order_ = order

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/shipment-classes/<int:shipment_class_id>")
def delete_shipment_classes_id(shipment_class_id: int) -> Response:
    with conn.begin() as s:
        # Get shipment_class
        # Raise if shipment_class doesn't exist
        shipment_class = s.query(ShipmentClass).filter_by(id=shipment_class_id).first()
        if not shipment_class:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        shipment_class.is_deleted = True

    return response()
