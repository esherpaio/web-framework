from enum import StrEnum

from flask import Response
from sqlalchemy.orm import Session

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.resource.cart_item import get_resource
from web.database.client import conn
from web.database.model import Cart, CartItem
from web.helper.api import ApiText, json_get, response
from web.helper.cart import get_shipment_methods, update_cart_count
from web.helper.security import get_access


class _Text(StrEnum):
    ADDED = "The product has been added to your cart."


@api_v1_bp.post("/carts/<int:cart_id>/items")
def post_carts_id_items(cart_id: int) -> Response:
    sku_id, has_sku_id = json_get("sku_id", int)

    data = {}

    with conn.begin() as s:
        # Authorize request
        # Get cart
        # Raise if cart doesn't exist
        access = get_access(s)
        cart = s.query(Cart).filter_by(access_id=access.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Update or insert cart item
        if has_sku_id:
            for cart_item in cart.items:
                if cart_item.sku_id == sku_id:
                    cart_item.quantity += 1
                    break
            else:
                cart_item = CartItem(cart_id=cart.id, sku_id=sku_id, quantity=1)
                s.add(cart_item)
            s.flush()
            s.expire_all()

        # Update shipment method
        _update_cart_shipment_methods(s, cart)
        # Update cart count
        cart_count = update_cart_count(s, cart)
        # Create resource
        data["cart_count"] = cart_count

    resource = get_resource(cart_id)
    return response(message=_Text.ADDED, data=resource)


@api_v1_bp.patch("/carts/<int:cart_id>/items/<int:cart_item_id>")
def patch_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    quantity, has_quantity = json_get("quantity", int)

    with conn.begin() as s:
        # Authorize request
        # Get cart
        # Raise if cart doesn't exist
        access = get_access(s)
        cart = s.query(Cart).filter_by(access_id=access.id, id=cart_id).first()
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
        _update_cart_shipment_methods(s, cart)
        # Update cart count
        update_cart_count(s, cart)

    return response()


@api_v1_bp.delete("/carts/<int:cart_id>/items/<int:cart_item_id>")
def delete_cart_id_items_id(cart_id: int, cart_item_id: int) -> Response:
    with conn.begin() as s:
        # Authorize request
        # Get cart
        # Raise if cart doesn't exist
        access = get_access(s)
        cart = s.query(Cart).filter_by(access_id=access.id, id=cart_id).first()
        if not cart:
            return response(403, ApiText.HTTP_403)

        # Delete cart item
        s.query(CartItem).filter_by(id=cart_item_id, cart_id=cart_id).delete()
        s.flush()

        # Update shipment methods
        _update_cart_shipment_methods(s, cart)
        # Update cart count
        update_cart_count(s, cart)

    return response()


def _update_cart_shipment_methods(s: Session, cart: Cart) -> None:
    shipment_methods = get_shipment_methods(s, cart)
    if shipment_methods:
        shipment_method = min(shipment_methods)
        cart.shipment_method_id = shipment_method.id
        cart.shipment_price = shipment_method.unit_price * cart.currency.rate
    else:
        cart.shipment_method_id = None
        cart.shipment_price = 0
    s.flush()
