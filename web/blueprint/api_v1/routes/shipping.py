from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.blueprint.api_v1.common.cart_item import update_cart_shipment_methods
from web.database.model import Cart, Order, Shipping

#
# Configuration
#


class ShippingAPI(API):
    model = Shipping
    post_columns = {
        Shipping.address,
        Shipping.city,
        Shipping.company,
        Shipping.country_id,
        Shipping.email,
        Shipping.first_name,
        Shipping.last_name,
        Shipping.phone,
        Shipping.zip_code,
    }
    patch_columns = {
        Shipping.address,
        Shipping.city,
        Shipping.company,
        Shipping.country_id,
        Shipping.email,
        Shipping.first_name,
        Shipping.last_name,
        Shipping.phone,
        Shipping.zip_code,
    }
    get_columns = {
        Shipping.address,
        Shipping.city,
        Shipping.company,
        Shipping.country_id,
        Shipping.email,
        Shipping.first_name,
        Shipping.id,
        Shipping.last_name,
        Shipping.phone,
        Shipping.user_id,
        Shipping.zip_code,
    }


def set_shipment_method(s: Session, data: dict, shipping: Shipping) -> None:
    carts = s.query(Cart).filter_by(shipping_id=shipping.id).all()
    for cart in carts:
        update_cart_shipment_methods(s, cart)


#
# Endpoints
#


@api_v1_bp.post("/shippings")
def post_shippings() -> Response:
    api = ShippingAPI()
    return api.post(
        add_request={"user_id": current_user.id},
    )


@api_v1_bp.get("/shippings/<int:shipping_id>")
def get_shippings_id(shipping_id: int) -> Response:
    api = ShippingAPI()
    return api.get(
        shipping_id,
        filters={Shipping.user_id == current_user.id},
    )


@api_v1_bp.patch("/shippings/<int:shipping_id>")
def patch_shippings_id(shipping_id: int) -> Response:
    api = ShippingAPI()
    api.raise_any_is_not_none({Order: {Order.shipping_id == shipping_id}})
    return api.patch(
        shipping_id,
        filters={Shipping.user_id == current_user.id},
        post_calls=[set_shipment_method],
    )
