import json

from sqlalchemy import false, null
from werkzeug import Response

from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import Order, OrderStatusId, Shipment, Sku, UserRoleLevel
from web.libs.api import json_get
from web.libs.auth import access_control
from web.mail import MailEvent, mail

#
# Helpers
#


OPEN_ORDER_FILTERS = (Order.status_id == OrderStatusId.READY,)
SKU_FILTERS = (Sku.number != null(), Sku.is_deleted == false())
ORDER_FILTERS = (Order.status_id.in_([OrderStatusId.READY, OrderStatusId.COMPLETED]),)


def response(code: int = 200, data: list | dict | None = None) -> Response:
    if data is None:
        data = {}
    return Response(json.dumps(data), status=code, mimetype="application/json")


#
# Routes
#


@webhook_v1_bp.get("/intime/open-orders/count")
@access_control(UserRoleLevel.EXTERNAL)
def intime_open_orders_count() -> Response:
    with conn.begin() as s:
        count = s.query(Order).filter(*OPEN_ORDER_FILTERS).count()
    return response(data={"count": count})


@webhook_v1_bp.get("/intime/open-orders/list")
@access_control(UserRoleLevel.EXTERNAL)
def intime_open_orders_list() -> Response:
    data = []
    with conn.begin() as s:
        orders = s.query(Order).filter(*OPEN_ORDER_FILTERS).all()
        for order in orders:
            data.append(
                {
                    "id": order.id,
                    "createdAt": order.created_at.isoformat(),
                    "recipient": {
                        "name": order.shipping.full_name,
                        "address": order.shipping.address,
                        "zip": order.shipping.zip_code,
                        "city": order.shipping.city,
                        "state": order.shipping.state,
                        "country": order.shipping.country.code,
                        "business": order.shipping.company,
                        "phone": order.shipping.phone,
                        "email": order.shipping.email,
                    },
                    "skus": [
                        {
                            "id": line.sku.number,
                            "name": line.sku.name,
                            "quantity": line.quantity,
                            "weight": 0,
                            "unitPrice": line.sku.unit_price,
                            "stock": line.sku.stock,
                            "productId": line.sku.product.id,
                            "variantId": line.sku.id,
                        }
                        for line in order.lines
                    ],
                }
            )
    return response(data=data)


@webhook_v1_bp.get("/intime/skus/<string:sku_number>/stock")
@access_control(UserRoleLevel.EXTERNAL)
def intime_skus_id_stock(sku_number: str) -> Response:
    with conn.begin() as s:
        sku = s.query(Sku).filter(Sku.number == sku_number, *SKU_FILTERS).first()
        if sku is None:
            return response(404)
    return response(data={"count": sku.stock})


@webhook_v1_bp.post("/intime/skus/<string:sku_number>/update-stock")
@access_control(UserRoleLevel.EXTERNAL)
def intime_skus_id(sku_number: str) -> Response:
    stock, _ = json_get("count", type_=int, nullable=False)
    with conn.begin() as s:
        sku = s.query(Sku).filter(Sku.number == sku_number, *SKU_FILTERS).first()
        if sku is None:
            return response(404)
        sku.stock = stock
    return response()


@webhook_v1_bp.get("/intime/skus/count")
@access_control(UserRoleLevel.EXTERNAL)
def intime_skus_count() -> Response:
    with conn.begin() as s:
        count = s.query(Sku).filter(*SKU_FILTERS).count()
    return response(data={"count": count})


@webhook_v1_bp.get("/intime/skus/list")
@access_control(UserRoleLevel.EXTERNAL)
def intime_skus_list() -> Response:
    data = []
    with conn.begin() as s:
        skus = s.query(Sku).filter(*SKU_FILTERS).all()
        for sku in skus:
            data.append(
                {
                    "id": sku.number,
                    "name": sku.name,
                    "weight": 0,
                    "unitPrice": sku.unit_price,
                    "stock": sku.stock,
                    "productId": sku.product.id,
                    "variantId": sku.id,
                }
            )
    return response(data=data)


@webhook_v1_bp.post("/intime/orders/<int:order_id>/fulfill")
@access_control(UserRoleLevel.EXTERNAL)
def intime_orders_id_fulfill(order_id: int) -> Response:
    with conn.begin() as s:
        order = s.query(Order).filter(Order.id == order_id, *ORDER_FILTERS).first()
        if order is None:
            return response(404)
        order.status_id = OrderStatusId.COMPLETED
    return response()


@webhook_v1_bp.post("/intime/orders/<int:order_id>/update-tracking")
@access_control(UserRoleLevel.EXTERNAL)
def intime_orders_id_update_tracking(order_id: int) -> Response:
    carrier, _ = json_get("carrierCode", type_=str)
    code, _ = json_get("trackingCode", type_=str, nullable=False)
    url, _ = json_get("trackingLink", type_=str, nullable=False)
    with conn.begin() as s:
        order = s.query(Order).filter(Order.id == order_id, *ORDER_FILTERS).first()
        if order is None:
            return response(404)
        # Update or create shipment
        shipment = next((s for s in order.shipments if s.code == code), None)
        if shipment is not None:
            shipment.carrier = carrier
            shipment.url = url
        else:
            shipment = Shipment(order_id=order.id, carrier=carrier, code=code, url=url)
            s.add(shipment)
            for event in mail.get_events(MailEvent.ORDER_SHIPPED):
                event(
                    order_id=order_id,
                    shipment_url=shipment.url,
                    billing_email=order.billing.email,
                    shipping_email=order.shipping.email,
                    shipping_address=order.shipping.full_address,
                )
        # Update order status
        order.status_id = OrderStatusId.COMPLETED
    return response()
