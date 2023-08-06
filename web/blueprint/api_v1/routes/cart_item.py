from enum import StrEnum

from flask import abort
from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.blueprint.api_v1.common.cart_item import update_cart_shipment_methods
from web.database.client import conn
from web.database.model import Cart, CartItem
from web.helper.api import ApiText, response
from web.i18n.base import _

#
# Configuration
#


class Text(StrEnum):
    CART_ITEM_ADDED = _("API_CART_ITEM_ADDED")


class CartItemAPI(API):
    model = CartItem
    post_columns = {
        CartItem.quantity,
        CartItem.sku_id,
    }
    patch_columns = {
        CartItem.quantity,
    }
    get_columns = {
        CartItem.cart_id,
        CartItem.id,
        CartItem.quantity,
        CartItem.sku_id,
    }


#
# Endpoints
#


@api_v1_bp.post("/carts/<int:cart_id>/items")
def post_carts_id_items(cart_id: int) -> Response:
    api = CartItemAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = update_or_insert_cart_item(s, data)
        update_cart(s, data)
        resource = api.gen_resource(s, model)
    return response(message=Text.CART_ITEM_ADDED, data=resource)


@api_v1_bp.patch("/carts/<int:cart_id>/items/<int:cart_item_id>")
def patch_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    api = CartItemAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        validate_cart(s, data)
        model = api.get(s, cart_item_id)
        api.update(s, data, model)
        update_cart(s, data)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.delete("/carts/<int:cart_id>/items/<int:cart_item_id>")
def delete_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    api = CartItemAPI()
    data = api.gen_view_args_data()
    with conn.begin() as s:
        model = api.get(s, cart_item_id)
        api.delete(s, model)
        update_cart(s, data)
    return response()


#
# Functions
#


def update_or_insert_cart_item(s: Session, data: dict) -> CartItem:
    cart_id = data["cart_id"]
    sku_id = data["sku_id"]
    quantity = data.get("quantity", 1)

    filters = {Cart.user_id == current_user.id, Cart.id == cart_id}
    cart = s.query(Cart).filter(*filters).first()
    if cart is None:
        abort(response(404, ApiText.HTTP_404))

    for cart_item in cart.items:
        if cart_item.sku_id == sku_id:
            cart_item.quantity += quantity
            model = cart_item
            break
    else:
        cart_item = CartItem(cart_id=cart.id, sku_id=sku_id, quantity=quantity)
        cart.items.append(cart_item)
        model = cart_item

    s.flush()
    return model


def validate_cart(s: Session, data: dict) -> None:
    cart_id = data["cart_id"]
    filters = {Cart.id == cart_id, Cart.user_id == current_user.id}
    cart = s.query(Cart).filter(*filters).first()
    if cart is None:
        abort(response(404, ApiText.HTTP_404))


def update_cart(s: Session, data: dict) -> None:
    cart_id = data["cart_id"]
    cart = s.query(Cart).filter(Cart.id == cart_id).first()
    if cart is not None:
        update_cart_shipment_methods(s, cart)
