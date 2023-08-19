from enum import StrEnum
from typing import Callable

from flask import redirect, url_for, request
from sqlalchemy.exc import IntegrityError
from werkzeug import Response
from werkzeug.exceptions import HTTPException

from web import config
from web.database.errors import DbEmailError, DbPhoneError
from web.helper.api import ApiText, response
from web.helper.logger import logger
from web.i18n.base import _


class _Text(StrEnum):
    EMAIL_ERROR = _("DATABASE_EMAIL_ERROR")
    PHONE_ERROR = _("DATABASE_PHONE_ERROR")


def handle_frontend_exception(f: Callable) -> Callable[[Exception], Response]:
    def wrap(error: Exception) -> Response:
        if isinstance(error, HTTPException):
            logger.warning(f"HTTP {error.code}: {error.description}")
        else:
            logger.error("", exc_info=True)
        return redirect(url_for(config.ENDPOINT_ERROR))

    wrap.__name__ = f.__name__
    return wrap


def handle_backend_exception(f: Callable) -> Callable[[Exception], Response]:
    def wrap(error: Exception) -> Response:
        code: int
        message: StrEnum
        if isinstance(error, IntegrityError):
            code, message = 409, ApiText.HTTP_409
        elif isinstance(error, DbEmailError):
            code, message = 400, _Text.EMAIL_ERROR
        elif isinstance(error, DbPhoneError):
            code, message = 400, _Text.PHONE_ERROR
        else:
            data = request.get_json() if request.is_json else None
            logger.error(f"Backend exception with data: {str(data)}", exc_info=True)
            code, message = 500, ApiText.HTTP_500
        return response(code, message)

    wrap.__name__ = f.__name__
    return wrap
