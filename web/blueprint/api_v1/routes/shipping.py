from flask import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.resource.shipping import get_resource
from web.database.client import conn
from web.database.model import Cart, Order, Shipping, User
from web.helper.api import ApiText, json_get, response
from web.helper.security import get_access


@api_v1_bp.post("/shippings")
def post_shippings() -> Response:
    address, _ = json_get("address", str, allow_empty=False)
    city, _ = json_get("city", str, allow_empty=False)
    company, _ = json_get("company", str, allow_empty=False)
    country_id, _ = json_get("country_id", int)
    email, _ = json_get("email", str, allow_empty=False)
    first_name, _ = json_get("first_name", str, allow_empty=False)
    last_name, _ = json_get("last_name", str, allow_empty=False)
    phone, _ = json_get("phone", str, allow_empty=False)
    zip_code, _ = json_get("zip_code", str, allow_empty=False)

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
        s.flush()

    resource = get_resource(shipping.id)
    return response(data=resource)


@api_v1_bp.get("/shippings/<int:shipping_id>")
def get_shippings_id(shipping_id: int) -> Response:
    with conn.begin() as s:
        # Authorize request
        # Raise if shipping_id not in use by user
        access = get_access(s)
        cart = (
            s.query(Cart)
            .filter_by(access_id=access.id, shipping_id=shipping_id)
            .first()
        )
        user = (
            s.query(User).filter_by(id=access.user_id, shipping_id=shipping_id).first()
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
    address, has_address = json_get("address", str, allow_empty=False)
    city, has_city = json_get("city", str, allow_empty=False)
    company, has_company = json_get("company", str, allow_empty=False)
    country_id, has_country_id = json_get("country_id", int)
    email, has_email = json_get("email", str, allow_empty=False)
    first_name, has_first_name = json_get("first_name", str, allow_empty=False)
    last_name, has_last_name = json_get("last_name", str, allow_empty=False)
    phone, has_phone = json_get("phone", str, allow_empty=False)
    zip_code, has_zip_code = json_get("zip_code", str, allow_empty=False)

    with conn.begin() as s:
        # Authorize request
        # Raise if shipping_id not in use by user
        access = get_access(s)
        cart = (
            s.query(Cart)
            .filter_by(access_id=access.id, shipping_id=shipping_id)
            .first()
        )
        user = (
            s.query(User).filter_by(id=access.user_id, shipping_id=shipping_id).first()
        )
        if cart is None and user is None:
            return response(403, ApiText.HTTP_403)

        # Check if billing is in use by an order
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
        s.flush()

    resource = get_resource(shipping_id)
    return response(data=resource)
