from enum import StrEnum

from sqlalchemy import null, true
from werkzeug import Response

from web.api import json_get
from web.api.response import json_response
from web.app.blueprint.api_v1 import api_v1_bp
from web.config import config
from web.database import conn
from web.database.model import User
from web.i18n import _
from web.mail import mail
from web.mail.enum import MailEvent

#
# Configuration
#


class Text(StrEnum):
    CONTACT_SUCCESS = _("API_MAIL_CONTACT_SUCCESS")
    EVENT_ID_INVALID = _("API_MAIL_INVALID_EVENT_ID")
    MAIL_ERROR = _("API_MAIL_ERROR")
    TOO_MANY_EMAILS = _("API_MAIL_TOO_MANY")
    CONTACT_ADMIN = _("API_MAIL_CONTACT_ADMIN")


#
# Endpoints
#


@api_v1_bp.post("/emails")
def post_emails() -> Response:
    event_id, _ = json_get("event_id", str)
    data, _ = json_get("data", dict, default={})

    with conn.begin() as s:
        # Inject emails for bulk email
        if event_id == MailEvent.WEBSITE_BULK:
            if not config.WORKER_ENABLED:
                return json_response(400, Text.CONTACT_ADMIN)
            if "emails" not in data:
                users = (
                    s.query(User)
                    .filter(
                        User.is_active == true(),
                        User.bulk_email == true(),
                        User.email != null(),
                    )
                    .all()
                )
                emails = set(user.email for user in users)
                if len(emails) > config.EMAIL_MAX_BULK_COUNT:
                    return json_response(400, Text.TOO_MANY_EMAILS)
                data["emails"] = list(emails)

        # Trigger email events
        result = mail.trigger_events(s, event_id, **data)

    if not result:
        return json_response(400, Text.MAIL_ERROR)
    return json_response(200, Text.CONTACT_SUCCESS)


#
# Functions
#
