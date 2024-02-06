from typing import Any

from sqlalchemy import false, null
from werkzeug import Response

from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import Order, OrderStatusId, Shipment, Sku, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control



@webhook_v1_bp.get("/intime/open-orders/count")
@access_control(UserRoleLevel.EXTERNAL)
def intime_open_orders_count() -> Response:
    with conn.begin() as s:
        count = s.query(Order).filter(Order.status_id == OrderStatusId.READY).count()
    data = {"count": count}
    return response(data=data)



@webhook_v1_bp.get("/intime/open-orders/list")
@access_control(UserRoleLevel.EXTERNAL)
def intime_open_orders_list() -> Response:
    data = []
    with conn.begin() as s:
        orders = s.query(Order).filter(Order.status_id == OrderStatusId.READY).all()
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
                        "countryCode": order.shipping.country.code,
                        "business": order.shipping.company,
                        "phone": order.shipping.phone,
                        "email": order.shipping.email,
                    },
                    "products": [
                        {
                            "sku": line.sku.number,
                            "name": line.sku.name,
                            "quantity": line.quantity,
                            "price": line.sku.unit_price,
                            "productId": line.sku.product.id,
                            "variantId": line.sku.slug,
                        }
                        for line in order.lines
                    ],
                }
            )
    return response(data=data)



@webhook_v1_bp.get("/intime/products/<int:product_id>/stock")
@access_control(UserRoleLevel.EXTERNAL)
def intime_products_id_stock(product_id: int) -> Response:
    data = {"count": 0}
    return response(data=data)



@webhook_v1_bp.patch("/intime/products/<int:product_id>/update-inventory")
@access_control(UserRoleLevel.EXTERNAL)
def intime_products_id(product_id: int) -> Response:
    return response()



@webhook_v1_bp.get("/intime/products/count")
@access_control(UserRoleLevel.EXTERNAL)
def intime_products_count() -> Response:
    with conn.begin() as s:
        count = (
            s.query(Sku).filter(Sku.number != null(), Sku.is_deleted == false()).count()
        )
    data = {"count": count}
    return response(data=data)



@webhook_v1_bp.get("/intime/products/list")
@access_control(UserRoleLevel.EXTERNAL)
def intime_products_list() -> Response:
    data = []
    with conn.begin() as s:
        skus = (
            s.query(Sku).filter(Sku.number != null(), Sku.is_deleted == false()).all()
        )
        for sku in skus:
            data.append(
                {
                    "sku": sku.number,
                    "name": sku.name,
                    "weightGram": 0,
                    "unitPrice": sku.unit_price,
                    "stockCount": 0,
                    "productId": sku.product.id,
                    "variantId": sku.slug,
                }
            )
    return response(data=data)



@webhook_v1_bp.post("/intime/orders/<int:order_id>/fulfill")
@access_control(UserRoleLevel.EXTERNAL)
def intime_orders_id_fulfill(order_id: int) -> Response:
    with conn.begin() as s:
        order = (
            s.query(Order)
            .filter(
                Order.id == order_id,
                Order.status_id.in_([OrderStatusId.READY, OrderStatusId.COMPLETED]),
            )
            .first()
        )
        if order is not None:
            order.status_id = OrderStatusId.COMPLETED
        else:
            return response(404, ApiText.HTTP_404)
    return response()



@webhook_v1_bp.patch("/intime/orders/<int:order_id>/update-tracking")
@access_control(UserRoleLevel.EXTERNAL)
def intime_orders_id_update_tracking(order_id: int) -> Response:
    carrier = json_get("carrierCode", type_=Any)
    code = json_get("trackingCode", type_=Any)
    url = json_get("trackingLink", type_=str, nullable=False)
    with conn.begin() as s:
        order = (
            s.query(Order)
            .filter(
                Order.id == order_id,
                Order.status_id.in_([OrderStatusId.READY, OrderStatusId.COMPLETED]),
            )
            .first()
        )
        if order is not None:
            for shipment in order.shipments:
                if shipment.code == code:
                    break
            order.status_id = OrderStatusId.COMPLETED
            shipment = Shipment(order_id=order.id, carrier=carrier, code=code, url=url)
            s.add(shipment)
        else:
            return response(404, ApiText.HTTP_404)
    return response()
