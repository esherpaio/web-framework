from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Order, OrderStatusId, Shipment, UserRoleLevel
from web.helper.api import json_get, response
from web.helper.user import access_control
from web.mail.routes.order import send_order_shipped


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/orders/<int:order_id>/shipments")
def post_orders_id_shipments(order_id: int) -> Response:
    url, _ = json_get("url", str, nullable=False)

    with conn.begin() as s:
        # Get order
        order = s.query(Order).filter_by(id=order_id).first()

        # Insert shipment
        shipment = Shipment(order_id=order_id, url=url)
        s.add(shipment)
        s.flush()

        # Update order
        order.status_id = OrderStatusId.COMPLETED
        s.flush()

        # Send email
        send_order_shipped(
            order_id=order_id,
            shipment_url=url,
            billing_email=order.billing.email,
            shipping_email=order.shipping.email,
            shipping_address=order.shipping.full_address,
        )

    return response()
