from enum import StrEnum

from flask import Response

from web.blueprint.api_v1 import api_v1_bp
from web.helper.api import json_get, response
from web.i18n.base import _
from web.mail.routes.contact import send_contact_business, send_contact_customer


class _Text(StrEnum):
    INVALID_TEMPLATE_ID = _("API_MAIL_INVALID_TEMPLATE_ID")


@api_v1_bp.post("/emails")
def post_emails_contact() -> Response:
    template_id, _ = json_get("template_id", str)
    data, _ = json_get("data", dict)

    if template_id == "contact":
        send_contact_business(**data)
        send_contact_customer(**data)
    else:
        return response(403, _Text.INVALID_TEMPLATE_ID)
    return response()
