from enum import StrEnum

from flask_login import current_user
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Email
from web.helper.api import json_get, response
from web.i18n.base import _
from web.mail.events import mail

#
# Configuration
#


class Text(StrEnum):
    CONTACT_SUCCESS = _("API_MAIL_CONTACT_SUCCESS")
    EVENT_ID_INVALID = _("API_MAIL_INVALID_EVENT_ID")


#
# Endpoints
#


@api_v1_bp.post("/emails")
def post_emails_contact() -> Response:
    event_id, _ = json_get("event_id", str)
    data, _ = json_get("data", dict, default={})

    with conn.begin() as s:
        email = Email(event_id=event_id, data=data, user_id=current_user.id)
        s.add(email)
        s.flush()
        for event in mail.get_events(event_id):
            event(**data)

    return response(200, Text.CONTACT_SUCCESS)


#
# Functions
#
