from sqlalchemy import and_, or_
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import ShipmentMethod, ShipmentZone, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control

#
# Configuration
#


#
# Endpoints
#


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/shipment-zones")
def post_shipment_zones() -> Response:
    country_id, _ = json_get("country_id", int)
    order, _ = json_get("order", int, nullable=False)
    region_id, _ = json_get("region_id", int)

    with conn.begin() as s:
        # Get or restore shipment zone
        shipment_zone = (
            s.query(ShipmentZone)
            .filter(
                or_(
                    and_(
                        ShipmentZone.country_id.is_(None),
                        ShipmentZone.region_id == region_id,
                    ),
                    and_(
                        ShipmentZone.country_id == country_id,
                        ShipmentZone.region_id.is_(None),
                    ),
                ),
            )
            .first()
        )
        if shipment_zone:
            if shipment_zone.is_deleted:
                shipment_zone.is_deleted = False
                return response()
            else:
                return response(409, ApiText.HTTP_409)

        # Insert shipment zone
        shipment_zone = ShipmentZone(
            order=order,
            country_id=country_id,
            region_id=region_id,
        )
        s.add(shipment_zone)

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/shipment-zones/<int:shipment_zone_id>")
def patch_shipment_zones_id(shipment_zone_id: int) -> Response:
    country_id, has_country_id = json_get("country_id", int)
    order, has_order = json_get("order", int)
    region_id, has_region_id = json_get("region_id", int)

    with conn.begin() as s:
        # Get shipment zone
        shipment_zone = s.query(ShipmentZone).filter_by(id=shipment_zone_id).first()
        if not shipment_zone:
            return response(404, ApiText.HTTP_404)

        # Update shipment zone
        if has_order:
            shipment_zone.order = order
        if has_country_id:
            shipment_zone.country_id = country_id
        if has_region_id:
            shipment_zone.region_id = region_id

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/shipment-zones/<int:shipment_zone_id>")
def delete_shipment_zones_id(shipment_zone_id: int) -> Response:
    with conn.begin() as s:
        # Delete shipment zone
        shipment_zone = s.query(ShipmentZone).filter_by(id=shipment_zone_id).first()
        if not shipment_zone:
            return response(404, ApiText.HTTP_404)
        shipment_zone.is_deleted = True

        # Delete shipment zones
        shipment_methods = (
            s.query(ShipmentMethod)
            .filter_by(zone_id=shipment_zone_id, is_deleted=False)
            .all()
        )
        for shipment_method in shipment_methods:
            shipment_method.is_deleted = True

    return response()


#
# Functions
#
