from enum import StrEnum

from flask_login import current_user
from sqlalchemy import null, true
from werkzeug import Response

from web.api.utils import json_get, response
from web.blueprint.api_v1 import api_v1_bp
from web.database import conn
from web.database.model import Email, EmailStatusId, User
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
        email = Email(event_id=event_id, data=data, user_id=current_user.id)
        s.add(email)
        s.flush()
        if event_id == MailEvent.WEBSITE_MASS and "emails" not in data:
            data["emails"] = set(
                user.email
                for user in s.query(User)
                .filter(
                    User.is_active == true(),
                    User.allow_mass_email == true(),
                    User.email != null(),
                )
                .all()
            )
        if mail.trigger_events(event_id, **data):
            email.status_id = EmailStatusId.SENT

    return response(200, Text.CONTACT_SUCCESS)


#
# Functions
#
