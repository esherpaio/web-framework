from enum import StrEnum

from sqlalchemy import null, true
from werkzeug import Response

from web.api import json_get, json_response
from web.app.blueprint import api_v1_bp
from web.database import conn
from web.database.model import User
from web.i18n import _
from web.mail import MailEvent, mail

#
# Configuration
#


class Text(StrEnum):
    CONTACT_SUCCESS = _("API_MAIL_CONTACT_SUCCESS")
    EVENT_ID_INVALID = _("API_MAIL_INVALID_EVENT_ID")
    MAIL_ERROR = _("API_MAIL_ERROR")


#
# Endpoints
#


@api_v1_bp.post("/emails")
def post_emails() -> Response:
    event_id, _ = json_get("event_id", str)
    data, _ = json_get("data", dict, default={})

    with conn.begin() as s:
        # Inject emails for bulk email
        if event_id == MailEvent.WEBSITE_BULK and "emails" not in data:
            users = (
                s.query(User)
                .filter(
                    User.is_active == true(),
                    User.bulk_email == true(),
                    User.email != null(),
                )
                .all()
            )
            data["emails"] = set(user.email for user in users)
        # Trigger email events
        result = mail.trigger_events(s, event_id, **data)

    if not result:
        return json_response(400, Text.MAIL_ERROR)
    return json_response(200, Text.CONTACT_SUCCESS)


#
# Functions
#
