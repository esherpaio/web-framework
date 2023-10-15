from enum import StrEnum

from flask import abort
from sqlalchemy.orm.session import Session
from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.client import conn
from web.database.model import Verification
from web.helper.api import response
from web.i18n.base import _

#
# Configuration
#


class Text(StrEnum):
    VERIFICATION_INVALID = _("API_VERIFICATION_INVALID")


class VerificationAPI(API):
    model = Verification
    get_args = {
        Verification.key,
    }
    get_columns = {
        Verification.id,
        Verification.key,
        Verification.user_id,
    }


#
# Endpoints
#


@api_v1_bp.get("/verifications")
def get_verifications() -> Response:
    api = VerificationAPI()
    data = api.gen_query_data(api.get_args)
    with conn.begin() as s:
        filters = api.gen_query_filters(data, required=True)
        models = api.list_(s, *filters, limit=1)
        for model in models:
            val_verification(s, data, model)
        resources = api.gen_resources(s, models)
    return response(data=resources)


#
# Functions
#


def val_verification(s: Session, data: dict, model: Verification) -> None:
    if not model.is_valid:
        abort(response(400, Text.VERIFICATION_INVALID))
