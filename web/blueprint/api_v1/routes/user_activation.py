import uuid
from enum import StrEnum

from flask import url_for
from werkzeug import Response

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import User, Verification
from web.helper.api import ApiText, json_get, response
from web.i18n.base import _
from web.mail.events import Mail, MailEvent

#
# Configuration
#


class Text(StrEnum):
    ACTIVATION_CHECK = _("API_USER_ACTIVATION_CHECK")
    ACTIVATION_SUCCESS = _("API_USER_ACTIVATION_SUCCESS")
    VERIFICATION_FAILED = _("API_USER_VERIFICATION_FAILED")


#
# Endpoints
#


@api_v1_bp.post("/users/<int:user_id>/activation")
def post_users_id_activation(user_id: int) -> Response:
    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Insert verification
        verification_key = str(uuid.uuid4())
        verification = Verification(user_id=user.id, key=verification_key)
        s.add(verification)
        s.flush()

        # Send email
        verification_url = url_for(
            config.ENDPOINT_LOGIN,
            verification_key=verification.key,
            _external=True,
        )
        mail = Mail()
        for event in mail.events[MailEvent.USER_REQUEST_VERIFICATION]:
            event(email=user.email, verification_url=verification_url)

    return response(200, message=Text.ACTIVATION_CHECK)


@api_v1_bp.patch("/users/<int:user_id>/activation")
def patch_users_id_activation(user_id: int) -> Response:
    verification_key, _ = json_get("verification_key", str)

    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Check verification
        verification = s.query(Verification).filter_by(key=verification_key).first()
        if verification is None:
            return response(401, Text.VERIFICATION_FAILED)
        if not verification.is_valid:
            return response(401, Text.VERIFICATION_FAILED)
        if verification.user_id != user_id:
            return response(401, Text.VERIFICATION_FAILED)

        # Update activation
        user.is_active = True
        s.delete(verification)

    return response(200, message=Text.ACTIVATION_SUCCESS)


#
# Functions
#
