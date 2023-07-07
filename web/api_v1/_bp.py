from enum import StrEnum

from flask import Blueprint, Response

from web.database.errors import DbEmailError, DbError, DbPhoneError
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


@api_v1_bp.errorhandler(DbError)
def error_handler_db(error: DbError) -> Response:
    if isinstance(error, DbEmailError):
        return response(400, _Text.EMAIL_ERROR)
    elif isinstance(error, DbPhoneError):
        return response(400, _Text.PHONE_ERROR)


@api_v1_bp.errorhandler(Exception)
@handle_backend_exception
def error_handler() -> Response:
    pass
