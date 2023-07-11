from flask import Response
from flask_login import current_user

from web.blueprints.api_v1 import api_v1_bp
from web.blueprints.api_v1.common.cart_item import update_cart_shipment_methods
from web.blueprints.api_v1.resource.shipping import get_resource
from web.database.client import conn
from web.database.model import Cart, Order, Shipping, User
from web.helper.api import ApiText, json_get, response


@api_v1_bp.post("/shippings")
def post_shippings() -> Response:
    address, _ = json_get("address", str, allow_empty_str=False)
    city, _ = json_get("city", str, allow_empty_str=False)
    company, _ = json_get("company", str, allow_empty_str=False)
    country_id, _ = json_get("country_id", int)
    email, _ = json_get("email", str, allow_empty_str=False)
    first_name, _ = json_get("first_name", str, allow_empty_str=False)
    last_name, _ = json_get("last_name", str, allow_empty_str=False)
    phone, _ = json_get("phone", str, allow_empty_str=False)
    zip_code, _ = json_get("zip_code", str, allow_empty_str=False)

    with conn.begin() as s:
        # Insert shipping
        shipping = Shipping(
            address=address,
            city=city,
            company=company,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            zip_code=zip_code,
            country_id=country_id,
        )
        s.add(shipping)

    resource = get_resource(shipping.id)
    return response(data=resource)


@api_v1_bp.get("/shippings/<int:shipping_id>")
def get_shippings_id(shipping_id: int) -> Response:
    with conn.begin() as s:
        # Check if shipping is in use by the user
        cart = (
            s.query(Cart)
            .filter_by(user_id=current_user.id, shipping_id=shipping_id)
            .first()
        )
        user = (
            s.query(User).filter_by(id=current_user.id, shipping_id=shipping_id).first()
        )
        if cart is None and user is None:
            return response(403, ApiText.HTTP_403)

        # Get shipping
        shipping = s.query(Shipping).filter_by(id=shipping_id).first()
        if not shipping:
            return response(404, ApiText.HTTP_404)

    resource = get_resource(shipping_id)
    return response(data=resource)


@api_v1_bp.patch("/shippings/<int:shipping_id>")
def patch_shippings_id(shipping_id: int) -> Response:
    address, has_address = json_get("address", str, allow_empty_str=False)
    city, has_city = json_get("city", str, allow_empty_str=False)
    company, has_company = json_get("company", str, allow_empty_str=False)
    country_id, has_country_id = json_get("country_id", int)
    email, has_email = json_get("email", str, allow_empty_str=False)
    first_name, has_first_name = json_get("first_name", str, allow_empty_str=False)
    last_name, has_last_name = json_get("last_name", str, allow_empty_str=False)
    phone, has_phone = json_get("phone", str, allow_empty_str=False)
    zip_code, has_zip_code = json_get("zip_code", str, allow_empty_str=False)

    with conn.begin() as s:
        # Check if shipping is in use by the user
        cart = (
            s.query(Cart)
            .filter_by(user_id=current_user.id, shipping_id=shipping_id)
            .first()
        )
        user = (
            s.query(User).filter_by(id=current_user.id, shipping_id=shipping_id).first()
        )
        if cart is None and user is None:
            return response(403, ApiText.HTTP_403)

        # Check if shipping is in use by an order
        order = s.query(Order).filter_by(shipping_id=shipping_id).first()
        if order:
            return response(403, ApiText.HTTP_403)

        # Get shipping
        shipping = s.query(Shipping).filter_by(id=shipping_id).first()
        if not shipping:
            return response(404, ApiText.HTTP_404)

        # Update shipping
        if has_address:
            shipping.address = address
        if has_city:
            shipping.city = city
        if has_company:
            shipping.company = company
        if has_email:
            shipping.email = email
        if has_first_name:
            shipping.first_name = first_name
        if has_last_name:
            shipping.last_name = last_name
        if has_phone:
            shipping.phone = phone
        if has_zip_code:
            shipping.zip_code = zip_code
        if has_country_id:
            shipping.country_id = country_id

        # Sync carts
        carts = s.query(Cart).filter_by(shipping_id=shipping.id).all()
        for cart in carts:
            update_cart_shipment_methods(s, cart)

    resource = get_resource(shipping_id)
    return response(data=resource)
