from enum import StrEnum

from flask import Response
from flask_login import current_user

from web.blueprints.api_v1 import api_v1_bp
from web.blueprints.api_v1.common.cart_item import update_cart_shipment_methods
from web.blueprints.api_v1.resource.cart_item import get_resource
from web.database.client import conn
from web.database.model import Cart, CartItem
from web.helper.api import ApiText, json_get, response
from web.i18n.base import _


class _Text(StrEnum):
    ADDED = _("API_CART_ITEM_ADDED")


@api_v1_bp.post("/carts/<int:cart_id>/items")
def post_carts_id_items(cart_id: int) -> Response:
    quantity, _ = json_get("quantity", int, default=1)
    sku_id, _ = json_get("sku_id", int, nullable=False)

    with conn.begin() as s:
        # Check if cart is in use by the user
        cart = s.query(Cart).filter_by(user_id=current_user.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Update or insert cart item
        for cart_item in cart.items:
            if cart_item.sku_id == sku_id:
                cart_item.quantity += quantity
                break
        else:
            cart_item = CartItem(cart_id=cart.id, sku_id=sku_id, quantity=quantity)
            cart.items.append(cart_item)
        s.flush()

        # Update shipment method
        update_cart_shipment_methods(s, cart)

    resource = get_resource(cart_item.id)
    return response(message=_Text.ADDED, data=resource)


@api_v1_bp.patch("/carts/<int:cart_id>/items/<int:cart_item_id>")
def patch_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    quantity, has_quantity = json_get("quantity", int)

    with conn.begin() as s:
        # Check if cart is in use by the user
        cart = s.query(Cart).filter_by(user_id=current_user.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Update quantity
        if has_quantity:
            if quantity < 1:
                return response(400, ApiText.HTTP_400)
            cart_item = (
                s.query(CartItem).filter_by(id=cart_item_id, cart_id=cart_id).first()
            )
            cart_item.quantity = quantity
        s.flush()

        # Update shipment methods
        update_cart_shipment_methods(s, cart)

    resource = get_resource(cart_item_id)
    return response(data=resource)


@api_v1_bp.delete("/carts/<int:cart_id>/items/<int:cart_item_id>")
def delete_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    with conn.begin() as s:
        # Check if cart is in use by the user
        cart = s.query(Cart).filter_by(user_id=current_user.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Delete cart item
        cart_item = (
            s.query(CartItem).filter_by(id=cart_item_id, cart_id=cart_id).first()
        )
        s.delete(cart_item)

        # Update shipment methods
        update_cart_shipment_methods(s, cart)

    return response()
