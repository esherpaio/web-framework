from werkzeug import Response

from web.api import API, ApiText, json_get, json_response
from web.app.blueprint.api_v1 import api_v1_bp
from web.auth import authorize
from web.database import conn
from web.database.model import ShipmentMethod, UserRoleLevel

#
# Configuration
#


class ShipmentMethodAPI(API):
    model = ShipmentMethod
    get_filters = {
        "cart_id",
    }
    get_columns = {
        ShipmentMethod.id,
        ShipmentMethod.name,
        ShipmentMethod.phone_required,
        ShipmentMethod.unit_price,
        ShipmentMethod.class_id,
        ShipmentMethod.zone_id,
    }


#
# Endpoints
#


@api_v1_bp.post("/shipment-methods")
@authorize(UserRoleLevel.ADMIN)
def post_shipment_methods() -> Response:
    class_id, _ = json_get("class_id", int, nullable=False)
    name, _ = json_get("name", str, nullable=False)
    phone_required, _ = json_get("phone_required", bool, default=False)
    unit_price, _ = json_get("unit_price", int | float, nullable=False)
    zone_id, _ = json_get("zone_id", int, nullable=False)

    with conn.begin() as s:
        # Insert shipment method
        shipment_method = ShipmentMethod(
            name=name,
            class_id=class_id,
            zone_id=zone_id,
            unit_price=unit_price,
            phone_required=phone_required,
        )
        s.add(shipment_method)

    return json_response()


@api_v1_bp.get("/shipment-methods")
def get_shipment_methods() -> Response:
    api = ShipmentMethodAPI()
    data = api.gen_query_data(api.get_filters)
    with conn.begin() as s:
        filters = api.gen_query_filters(data, required=True)
        filters.add(ShipmentMethod.is_deleted == False)  # noqa: E712
        models: list[ShipmentMethod] = api.list_(s, *filters)
        resources = api.gen_resources(s, models)
    return json_response(data=resources)


@api_v1_bp.patch("/shipment-methods/<int:shipment_method_id>")
@authorize(UserRoleLevel.ADMIN)
def patch_shipment_methods_id(shipment_method_id: int) -> Response:
    name, has_name = json_get("name", str)
    phone_required, has_phone_required = json_get("phone_required", bool)
    unit_price, has_unit_price = json_get("unit_price", int | float)

    with conn.begin() as s:
        # Get shipment method
        shipment_method = (
            s.query(ShipmentMethod).filter_by(id=shipment_method_id).first()
        )
        if not shipment_method:
            return json_response(404, ApiText.HTTP_404)

        # Update shipment method
        if has_name:
            shipment_method.name = name
        if has_unit_price:
            shipment_method.unit_price = unit_price
        if has_phone_required:
            shipment_method.phone_required = phone_required

    return json_response()


@api_v1_bp.delete("/shipment-methods/<int:shipment_method_id>")
@authorize(UserRoleLevel.ADMIN)
def delete_shipment_methods_id(shipment_method_id: int) -> Response:
    with conn.begin() as s:
        # Delete shipment method
        shipment_method = (
            s.query(ShipmentMethod).filter_by(id=shipment_method_id).first()
        )
        if shipment_method is None:
            return json_response(404, ApiText.HTTP_404)
        shipment_method.is_deleted = True

    return json_response()


#
# Functions
#
