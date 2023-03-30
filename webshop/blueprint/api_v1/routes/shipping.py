from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.blueprint.api_v1.resources.shipping import get_resource
from webshop.database.client import Conn
from webshop.database.model import Shipping, Cart, User
from webshop.helper.api import response, ApiText, json_get, json_empty_str_to_none
from webshop.helper.security import get_access


@api_v1_bp.post("/shippings")
@json_empty_str_to_none
def post_shippings() -> Response:
    address, _ = json_get("address", str)
    city, _ = json_get("city", str)
    company, _ = json_get("company", str)
    email, _ = json_get("email", str)
    first_name, _ = json_get("first_name", str)
    last_name, _ = json_get("last_name", str)
    phone, _ = json_get("phone", str)
    zip_code, _ = json_get("zip_code", str)
    country_id, _ = json_get("country_id", int)

    with Conn.begin() as s:
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
    with Conn.begin() as s:
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
@json_empty_str_to_none
def patch_shippings_id(shipping_id: int) -> Response:
    address, has_address = json_get("address", str)
    city, has_city = json_get("city", str)
    company, has_company = json_get("company", str)
    email, has_email = json_get("email", str)
    first_name, has_first_name = json_get("first_name", str)
    last_name, has_last_name = json_get("last_name", str)
    phone, has_phone = json_get("phone", str)
    zip_code, has_zip_code = json_get("zip_code", str)
    country_id, has_country_id = json_get("country_id", int)

    with Conn.begin() as s:
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
