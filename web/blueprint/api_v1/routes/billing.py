from flask import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.resource.billing import get_resource
from web.database.client import conn
from web.database.model import Billing, Cart, Order, User
from web.helper.api import ApiText, json_get, response
from web.helper.cart import get_vat
from web.helper.security import get_access


@api_v1_bp.post("/billings")
def post_billings() -> Response:
    address, _ = json_get("address", str, allow_empty_str=False)
    city, _ = json_get("city", str, allow_empty_str=False)
    company, _ = json_get("company", str, allow_empty_str=False)
    country_id, _ = json_get("country_id", int)
    email, _ = json_get("email", str, allow_empty_str=False)
    first_name, _ = json_get("first_name", str, allow_empty_str=False)
    last_name, _ = json_get("last_name", str, allow_empty_str=False)
    phone, _ = json_get("phone", str, allow_empty_str=False)
    vat, _ = json_get("vat", str, allow_empty_str=False)
    zip_code, _ = json_get("zip_code", str, allow_empty_str=False)

    with conn.begin() as s:
        # Insert billing
        billing = Billing(
            address=address,
            city=city,
            company=company,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            vat=vat,
            zip_code=zip_code,
            country_id=country_id,
        )
        s.add(billing)
        s.flush()

    resource = get_resource(billing.id)
    return response(data=resource)


@api_v1_bp.patch("/billings/<int:billing_id>")
def patch_billings(billing_id: int) -> Response:
    address, has_address = json_get("address", str, allow_empty_str=False)
    city, has_city = json_get("city", str, allow_empty_str=False)
    company, has_company = json_get("company", str, allow_empty_str=False)
    country_id, has_country_id = json_get("country_id", int)
    email, has_email = json_get("email", str, allow_empty_str=False)
    first_name, has_first_name = json_get("first_name", str, allow_empty_str=False)
    last_name, has_last_name = json_get("last_name", str, allow_empty_str=False)
    phone, has_phone = json_get("phone", str, allow_empty_str=False)
    vat, has_vat = json_get("vat", str, allow_empty_str=False)
    zip_code, has_zip_code = json_get("zip_code", str, allow_empty_str=False)

    with conn.begin() as s:
        # Authorize request
        # Raise if id not in use by user
        access = get_access(s)
        cart = (
            s.query(Cart).filter_by(access_id=access.id, billing_id=billing_id).first()
        )
        user = s.query(User).filter_by(id=access.user_id, billing_id=billing_id).first()
        if cart is None and user is None:
            return response(403, ApiText.HTTP_403)

        # Check if billing is in use by an order
        order = s.query(Order).filter_by(billing_id=billing_id).first()
        if order:
            return response(403, ApiText.HTTP_403)

        # Get billing
        billing = s.query(Billing).filter_by(id=billing_id).first()
        if not billing:
            return response(404, ApiText.HTTP_404)

        # Update billing
        if has_address:
            billing.address = address
        if has_city:
            billing.city = city
        if has_company:
            billing.company = company
        if has_email:
            billing.email = email
        if has_first_name:
            billing.first_name = first_name
        if has_last_name:
            billing.last_name = last_name
        if has_phone:
            billing.phone = phone
        if has_vat:
            billing.vat = vat
        if has_zip_code:
            billing.zip_code = zip_code
        if has_country_id:
            billing.country_id = country_id
        s.flush()

        # Sync carts
        carts = s.query(Cart).filter_by(billing_id=billing.id).all()
        for cart in carts:
            country_code = billing.country.code
            is_business = billing.company is not None
            vat_rate, vat_reverse = get_vat(country_code, is_business)
            cart.currency_id = billing.country.currency_id
            cart.vat_rate = vat_rate
            cart.vat_reverse = vat_reverse
            s.flush()

    resource = get_resource(billing_id)
    return response(data=resource)
