from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.helper.api import response, json_get
from webshop.mail.routes.contact import send_contact


@api_v1_bp.post("/emails/contact")
def post_emails_contact() -> Response:
    company, _ = json_get("company", str)
    email, _ = json_get("email", str, nullable=False)
    message, _ = json_get("message", str, nullable=False)
    name, _ = json_get("name", str, nullable=False)
    phone, _ = json_get("phone", str)

    send_contact(
        email=email,
        name=name,
        message=message,
        company=company,
        phone=phone,
    )

    return response()
