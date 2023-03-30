from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.database.client import Conn
from webshop.database.model import ShipmentMethod
from webshop.database.model.user_role import UserRoleLevel
from webshop.helper.api import response, ApiText, json_get
from webshop.helper.security import authorize


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/shipment-methods")
def post_shipment_methods() -> Response:
    class_id, _ = json_get("class_id", int, nullable=False)
    name, _ = json_get("name", str, nullable=False)
    phone_required, _ = json_get("phone_required", bool, default=False)
    unit_price, _ = json_get("unit_price", int | float, nullable=False)
    zone_id, _ = json_get("zone_id", int, nullable=False)

    with Conn.begin() as s:
        # Insert shipment_method
        shipment_method = ShipmentMethod(
            name=name,
            class_id=class_id,
            zone_id=zone_id,
            unit_price=unit_price,
            phone_required=phone_required,
        )
        s.add(shipment_method)

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/shipment-methods/<int:shipment_method_id>")
def patch_shipment_methods_id(shipment_method_id: int) -> Response:
    name, has_name = json_get("name", str)
    phone_required, has_phone_required = json_get("phone_required", bool)
    unit_price, has_unit_price = json_get("unit_price", int | float)

    with Conn.begin() as s:
        # Get shipment_method
        # Raise if shipment_method doesn't exist
        shipment_method = (
            s.query(ShipmentMethod).filter_by(id=shipment_method_id).first()
        )
        if not shipment_method:
            return response(404, ApiText.HTTP_404)

        # Update name
        if has_name:
            shipment_method.name = name

        # Update unit_price
        if has_unit_price:
            shipment_method.unit_price = unit_price

        # Update phone_required
        if has_phone_required:
            shipment_method.phone_required = phone_required

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/shipment-methods/<int:shipment_method_id>")
def delete_shipment_methods_id(shipment_method_id: int) -> Response:
    with Conn.begin() as s:
        # Get shipment_method
        # Raise if shipment_method doesn't exist
        shipment_method = (
            s.query(ShipmentMethod).filter_by(id=shipment_method_id).first()
        )
        if shipment_method is None:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        shipment_method.is_deleted = True

    return response()
