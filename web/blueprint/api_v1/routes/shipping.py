from flask import abort
from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.blueprint.api_v1._common import update_cart_shipment_methods
from web.database.client import conn
from web.database.model import Cart, Order, Shipping
from web.helper.api import ApiText, response

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


#
# Endpoints
#


@api_v1_bp.post("/shippings")
def post_shippings() -> Response:
    api = ShippingAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = api.model()
        set_user_id(s, data, model)
        api.insert(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.get("/shippings/<int:shipping_id>")
def get_shippings_id(shipping_id: int) -> Response:
    api = ShippingAPI()
    with conn.begin() as s:
        filters = {Shipping.user_id == current_user.id}
        model = api.get(s, shipping_id, *filters)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.patch("/shippings/<int:shipping_id>")
def patch_shippings_id(shipping_id: int) -> Response:
    api = ShippingAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        filters = {Shipping.user_id == current_user.id}
        model = api.get(s, shipping_id, *filters)
        check_order(s, data, model)
        api.update(s, data, model)
        update_cart(s, data, model)
        resource = api.gen_resource(s, model)
    return response(data=resource)


#
# Functions
#


def set_user_id(s: Session, data: dict, shipping: Shipping) -> None:
    shipping.user_id = current_user.id


def update_cart(s: Session, data: dict, shipping: Shipping) -> None:
    cart = s.query(Cart).filter_by(shipping_id=shipping.id).first()
    if cart is not None:
        update_cart_shipment_methods(s, cart)


def check_order(s: Session, data: dict, shipping: Shipping) -> None:
    filters = {Order.shipping_id == shipping.id}
    order = s.query(Order).filter(*filters).first()
    if order is not None:
        abort(response(404, ApiText.HTTP_404))
