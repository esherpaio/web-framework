from enum import StrEnum

from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.helper.api import json_get, response
from web.i18n.base import _
from web.mail.routes.contact import send_contact_business, send_contact_customer
from web.mail.routes.custom import send_custom_1


class _Text(StrEnum):
    CONTACT_SUCCESS = _("API_MAIL_CONTACT_SUCCESS")
    TEMPLATE_ID_INVALID = _("API_MAIL_INVALID_TEMPLATE_ID")


@api_v1_bp.post("/emails")
def post_emails_contact() -> Response:
    template_id, _ = json_get("template_id", str)
    data, _ = json_get("data", dict)

    if template_id == "contact":
        send_contact_business(**data)
        send_contact_customer(email=data["email"], message=data["message"])
        return response(200, _Text.CONTACT_SUCCESS)
    elif template_id == "custom_1":
        send_custom_1(**data)
        send_contact_customer(email=data["email"], message=data["message"])
        return response(200, _Text.CONTACT_SUCCESS)

    return response(403, _Text.TEMPLATE_ID_INVALID)
