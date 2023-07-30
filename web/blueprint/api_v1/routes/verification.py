from enum import StrEnum

from flask import abort
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Verification
from web.helper.api import response
from web.i18n.base import _


class _Text(StrEnum):
    VERIFICATION_INVALID = _("API_VERIFICATION_INVALID")


class VerificationAPI(API):
    model = Verification
    get_args = {
        Verification.key,
    }
    get_args_required = {
        Verification.key,
    }
    get_columns = {
        Verification.id,
        Verification.key,
        Verification.user_id,
    }


@api_v1_bp.get("/verifications")
def get_verifications() -> Response:
    def validate(s: Session, verification: Verification, data: dict) -> None:
        if not verification.is_valid:
            abort(response(400, _Text.VERIFICATION_INVALID))

    api = VerificationAPI()
    return api.get(as_list=True, max_size=1, post_calls=[validate])
