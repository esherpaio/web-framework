from enum import StrEnum

from flask import abort
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import Verification
from web.helper.api import response
from web.i18n.base import _


def check_is_valid(s: Session, verification: Verification) -> None:
    if not verification.is_valid:
        abort(response(400, _Text.VERIFICATION_INVALID))


class _Text(StrEnum):
    VERIFICATION_INVALID = _("API_VERIFICATION_INVALID")


class VerificationAPI(API):
    model = Verification
    get_args = {Verification.key}
    get_attrs = {Verification.id, Verification.key, Verification.user_id}
    get_callbacks = [check_is_valid]


@api_v1_bp.get("/verifications")
def get_verifications() -> Response:
    api = VerificationAPI()
    return api.get(as_list=True)
