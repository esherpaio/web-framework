from enum import StrEnum

from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.resource.verification import get_resource
from web.database.client import conn
from web.database.model import Verification
from web.helper.api import args_get, response
from web.i18n.base import _


class _Text(StrEnum):
    VERIFICATION_INVALID = _("API_VERIFICATION_INVALID")
    VERIFICATION_KEY_NOT_FOUND = _("API_VERIFICATION_KEY_NOT_FOUND")


@api_v1_bp.get("/verifications")
def get_verifications() -> Response:
    key, _ = args_get("key", str)

    with conn.begin() as s:
        # Get verification
        verification = s.query(Verification).filter_by(key=key).first()
        if verification is None:
            return response(404, _Text.VERIFICATION_KEY_NOT_FOUND)

        # Check verification
        if not verification.is_valid:
            return response(400, _Text.VERIFICATION_INVALID)

    resource = [get_resource(verification.id)]
    return response(data=resource)
