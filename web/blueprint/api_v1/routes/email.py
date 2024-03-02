from enum import StrEnum

from sqlalchemy import null, true
from werkzeug import Response

from web.api.utils import json_get, response
from web.blueprint.api_v1 import api_v1_bp
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
        mail.trigger_events(s, event_id, **data)

    return response(200, Text.CONTACT_SUCCESS)


#
# Functions
#
