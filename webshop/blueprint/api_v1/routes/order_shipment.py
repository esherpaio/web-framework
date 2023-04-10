from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.database.client import Conn
from webshop.database.model import Order, Shipment, OrderStatusId, UserRoleLevel
from webshop.helper.api import response, json_get
from webshop.helper.security import authorize
from webshop.mail.routes.order import send_order_shipped


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/orders/<int:order_id>/shipments")
def post_orders_id_shipments(order_id: int) -> Response:
    url, _ = json_get("url", str, nullable=False)

    with Conn.begin() as s:
        # Get order
        order = s.query(Order).filter_by(id=order_id).first()

        # Create payment
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
