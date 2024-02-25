import json

from sqlalchemy import false, null
from sqlalchemy.orm import joinedload
from werkzeug import Response

from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import (
    Order,
    OrderLine,
    OrderStatusId,
    Shipment,
    Shipping,
    Sku,
    UserRoleLevel,
)
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


@webhook_v1_bp.get("/intime/products/count")
@access_control(UserRoleLevel.EXTERNAL)
def intime_skus_count() -> Response:
    with conn.begin() as s:
        count = s.query(Sku).filter(*SKU_FILTERS).count()
    return response(data={"count": count})


@webhook_v1_bp.get("/intime/products/list")
@access_control(UserRoleLevel.EXTERNAL)
def intime_skus_list() -> Response:
    products = []
    with conn.begin() as s:
        # Fetch skus
        skus = s.query(Sku).options(joinedload(Sku.product)).filter(*SKU_FILTERS).all()
        # Serialize skus
        for sku in skus:
            products.append(
                {
                    "id": str(sku.product.id),
                    "variantId": str(sku.id),
                    "sku": sku.number,
                    "name": sku.name,
                    "createdAt": sku.created_at.isoformat(),
                    "updatedAt": sku.updated_at.isoformat(),
                    "weightInGrams": 0,
                    "unitPrice": sku.unit_price,
                    "stock": sku.stock,
                }
            )
    return response(data={"products": products})


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
        has_updated = bool(s.is_modified(sku))
    return response(data={"hasUpdated": has_updated})


@webhook_v1_bp.get("/intime/open-orders/count")
@access_control(UserRoleLevel.EXTERNAL)
def intime_open_orders_count() -> Response:
    with conn.begin() as s:
        count = s.query(Order).filter(*OPEN_ORDER_FILTERS).count()
    return response(data={"count": count})


@webhook_v1_bp.get("/intime/open-orders/list")
@access_control(UserRoleLevel.EXTERNAL)
def intime_open_orders_list() -> Response:
    open_orders = []
    with conn.begin() as s:
        # Fetch orders
        orders = (
            s.query(Order)
            .options(
                joinedload(Order.lines),
                joinedload(Order.lines, OrderLine.sku),
                joinedload(Order.lines, OrderLine.sku, Sku.product),
                joinedload(Order.shipping),
                joinedload(Order.shipping, Shipping.country),
            )
            .filter(*OPEN_ORDER_FILTERS)
            .all()
        )
        # Serialize orders
        for order in orders:
            open_orders.append(
                {
                    "id": str(order.id),
                    "createdAt": order.created_at.isoformat(),
                    "updatedAt": order.updated_at.isoformat(),
                    "shippingUpgrade": order.shipment_name,
                    "recipient": {
                        "name": order.shipping.full_name,
                        "address": order.shipping.address,
                        "zipCode": order.shipping.zip_code,
                        "city": order.shipping.city,
                        "state": order.shipping.state,
                        "countryCode": order.shipping.country.code,
                        "companyName": order.shipping.company,
                        "phone": order.shipping.phone,
                        "email": order.shipping.email,
                    },
                    "items": [
                        {
                            "id": str(line.id),
                            "productId": str(line.sku.product.id),
                            "variantId": str(line.sku.id),
                            "sku": line.sku.number,
                            "name": line.sku.name,
                            "quantity": line.quantity,
                            "weightInGrams": 0,
                            "unitPrice": line.sku.unit_price,
                            "stock": line.sku.stock,
                        }
                        for line in order.lines
                    ],
                }
            )
    return response(data={"openOrders": open_orders})


@webhook_v1_bp.post("/intime/orders/<string:order_id>/update-tracking")
@access_control(UserRoleLevel.EXTERNAL)
def intime_orders_id_update_tracking(order_id: str) -> Response:
    # Parse request
    carrier, _ = json_get("carrierCode", type_=str)
    code, _ = json_get("trackingCode", type_=str, nullable=False)
    url, _ = json_get("trackingLink", type_=str, nullable=False)
    with conn.begin() as s:
        # Fetch order
        order = (
            s.query(Order)
            .options(
                joinedload(Order.shipments),
                joinedload(Order.billing),
                joinedload(Order.shipping),
                joinedload(Order.shipping, Shipping.country),
            )
            .filter(Order.id == int(order_id), *ORDER_FILTERS)
            .first()
        )
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
        # Update order status
        order.status_id = OrderStatusId.COMPLETED
        # Evaluate updated
        has_updated = bool(s.is_modified(order) or s.is_modified(shipment) or s.new)
        # Send emails
        if has_updated:
            mail.trigger_events(
                MailEvent.ORDER_SHIPPED,
                order_id=order.id,
                shipment_url=url,
                billing_email=order.billing.email,
                shipping_email=order.shipping.email,
                shipping_address=order.shipping.full_address,
            )
    return response(data={"hasUpdated": has_updated})


@webhook_v1_bp.post("/intime/orders/<string:order_id>/fulfill")
@access_control(UserRoleLevel.EXTERNAL)
def intime_orders_id_fulfill(order_id: str) -> Response:
    with conn.begin() as s:
        order = s.query(Order).filter(Order.id == int(order_id), *ORDER_FILTERS).first()
        if order is None:
            return response(404)
        order.status_id = OrderStatusId.COMPLETED
        has_fulfilled = True
    return response(data={"hasFulfilled": has_fulfilled})
