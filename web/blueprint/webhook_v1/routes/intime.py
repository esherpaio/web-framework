from werkzeug import Response
from sqlalchemy import false

from web.blueprint.webhook_v1 import webhook_v1_bp
from web.database.client import conn
from web.database.model import Order, OrderStatusId, Sku
from web.helper.api import response, ApiText


@webhook_v1_bp.get("/intime/open-orders/count")
def intime_open_orders_count() -> Response:
    with conn.begin() as s:
        count = s.query(Order).filter(Order.status_id == OrderStatusId.READY).count()
    data = {"count": count}
    return response(data=data)


@webhook_v1_bp.get("/intime/open-orders/list")
def intime_open_orders_list() -> Response:
    data = []
    with conn.begin() as s:
        orders = s.query(Order).filter(Order.status_id == OrderStatusId.READY).all()
        for order in orders:
            data.append(
                {
                    "id": order.id,
                    "created_at": order.created_at.isoformat(),
                    "recipient": {
                        "name": order.shipping.full_name,
                        "address": order.shipping.address,
                        "zip": order.shipping.zip_code,
                        "city": order.shipping.city,
                        "state": order.shipping.state,
                        "country_code": order.shipping.country.code,
                        "business": order.shipping.company,
                        "phone": order.shipping.phone,
                        "email": order.shipping.email,
                    },
                    "products": [
                        {
                            "sku": line.sku.id,
                            "name": line.sku.name,
                            "quantity": line.quantity,
                            "price": line.sku.unit_price,
                            "product_id": line.sku.product.id,
                            "variant_id": line.sku.slug,
                        }
                        for line in order.lines
                    ],
                }
            )
    return response(data=data)


@webhook_v1_bp.get("/intime/products/<int:product_id>/stock")
def intime_products_id_stock(product_id: int) -> Response:
    data = {"count": 0}
    return response(data=data)


@webhook_v1_bp.patch("/intime/products/<int:product_id>/update-inventory")
def intime_products_id(product_id: int) -> Response:
    return response()


@webhook_v1_bp.get("/intime/products/count")
def intime_products_count() -> Response:
    with conn.begin() as s:
        count = s.query(Sku).filter(Sku.is_deleted == false()).count()
    data = {"count": count}
    return response(data=data)


@webhook_v1_bp.get("/intime/products/list")
def intime_products_list() -> Response:
    data = []
    with conn.begin() as s:
        skus = s.query(Sku).filter(Sku.is_deleted == false()).all()
        for sku in skus:
            data.append(
                {
                    "sku": sku.id,
                    "name": sku.name,
                    "weight": 0,
                    "price": sku.unit_price,
                    "stock_count": 0,
                    "product_id": sku.product.id,
                    "variant_id": sku.slug,
                }
            )
    return response(data=data)


@webhook_v1_bp.post("/intime/orders/<int:order_id>/fulfill")
def intime_orders_id_fulfill(order_id: int) -> Response:
    with conn.begin() as s:
        order = s.query(Order).filter_by(id=order_id, status_id=OrderStatusId.READY).first()
        if order is not None:
            order.status_id = OrderStatusId.COMPLETED
        else:
            return response(404, ApiText.HTTP_404)
    return response()


@webhook_v1_bp.patch("/intime/orders/<int:order_id>/update-tracking")
def intime_orders_id_update_tracking(order_id: int) -> Response:
    
    return response()
