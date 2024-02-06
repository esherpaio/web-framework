from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Order, OrderStatusId, Shipment, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control
from web.mail.base import MailEvent, mail

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/orders/<int:order_id>/shipments")
@access_control(UserRoleLevel.ADMIN)
def post_orders_id_shipments(order_id: int) -> Response:
    url, _ = json_get("url", str, nullable=False)

    with conn.begin() as s:
        # Get order
        order = s.query(Order).filter_by(id=order_id).first()
        if order is None:
            return response(404, ApiText.HTTP_404)

        # Insert shipment
        shipment = Shipment(order_id=order_id, url=url)
        s.add(shipment)
        s.flush()

        # Update order
        order.status_id = OrderStatusId.COMPLETED
        s.flush()

        # Send email
        for event in mail.get_events(MailEvent.ORDER_SHIPPED):
            event(
                order_id=order_id,
                shipment_url=url,
                billing_email=order.billing.email,
                shipping_email=order.shipping.email,
                shipping_address=order.shipping.full_address,
            )

    return response()


#
# Functions
#
