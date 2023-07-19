from enum import StrEnum

from flask import Blueprint
from werkzeug import Response

from web.database.errors import DbEmailError, DbPhoneError
from web.helper.api import response
from web.helper.errors import handle_backend_exception
from web.i18n.base import _

api_v1_bp = Blueprint(
    name="api_v1",
    import_name=__name__,
    url_prefix="/api/v1",
)


class _Text(StrEnum):
    EMAIL_ERROR = _("DATABASE_EMAIL_ERROR")
    PHONE_ERROR = _("DATABASE_PHONE_ERROR")


@api_v1_bp.errorhandler(DbEmailError)
def error_email(error: DbEmailError) -> Response:
    return response(400, _Text.EMAIL_ERROR)


@api_v1_bp.errorhandler(DbPhoneError)
def error_phone(error: DbPhoneError) -> Response:
    return response(400, _Text.PHONE_ERROR)


@api_v1_bp.errorhandler(Exception)
@handle_backend_exception
def error_handler() -> None:
    return None
