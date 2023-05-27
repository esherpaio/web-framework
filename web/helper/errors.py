from typing import Callable

from flask import Response, redirect, url_for
from werkzeug.exceptions import HTTPException

from web import config
from web.database.errors import DbEmailError, DbPhoneError
from web.helper.api import ApiText, response
from web.helper.logger import logger


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
        if isinstance(error, (DbEmailError, DbPhoneError)):
            message = error.MESSAGE
        else:
            message = ApiText.HTTP_500
            logger.error("", exc_info=True)
        return response(500, message)

    wrap.__name__ = f.__name__
    return wrap
