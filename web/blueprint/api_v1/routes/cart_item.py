from enum import StrEnum

from flask_login import current_user
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.blueprint.api_v1.common.cart_item import update_cart_shipment_methods
from web.database.model import Cart, CartItem
from web.i18n.base import _

#
# Configuration
#


class _Text(StrEnum):
    CART_ITEM_ADDED = _("API_CART_ITEM_ADDED")


class CartItemAPI(API):
    model = CartItem
    post_columns = {
        CartItem.quantity,
        CartItem.sku_id,
    }
    post_message = _Text.CART_ITEM_ADDED
    patch_columns = {CartItem.quantity}
    get_columns = {
        CartItem.cart_id,
        CartItem.id,
        CartItem.quantity,
        CartItem.sku_id,
    }


def update_shipment_methods(s: Session, data: dict, *args) -> None:
    cart_id = data["cart_id"]
    cart = s.query(Cart).filter(Cart.id == cart_id).first()
    update_cart_shipment_methods(s, cart)


#
# Endpoints
#


@api_v1_bp.post("/carts/<int:cart_id>/items")
def post_carts_id_items(cart_id: int) -> Response:
    api = CartItemAPI()
    api.raise_any_is_none({Cart: {Cart.id == cart_id, Cart.user_id == current_user.id}})
    return api.post(
        add_request={"cart_id": cart_id},
        post_calls=[update_shipment_methods],
    )


@api_v1_bp.patch("/carts/<int:cart_id>/items/<int:cart_item_id>")
def patch_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    api = CartItemAPI()
    api.raise_any_is_none({Cart: {Cart.id == cart_id, Cart.user_id == current_user.id}})
    return api.patch(
        cart_item_id,
        post_calls=[update_shipment_methods],
    )


@api_v1_bp.delete("/carts/<int:cart_id>/items/<int:cart_item_id>")
def delete_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    api = CartItemAPI()
    api.raise_any_is_none({Cart: {Cart.id == cart_id, Cart.user_id == current_user.id}})
    return api.delete(
        cart_item_id,
        post_calls=[update_shipment_methods],
    )
