from typing import Callable

from flask import redirect, request, url_for
from sqlalchemy.exc import IntegrityError
from werkzeug import Response
from werkzeug.exceptions import HTTPException

from web import config
from web.helper.api import ApiText, response
from web.helper.exceptions import WebError
from web.helper.logger import logger
from web.i18n.base import _

#
# Decorators
#


def handle_frontend_error(f: Callable) -> Callable[[Exception], Response]:
    """Decorator to handle frontend errors."""

    def wrap(error: Exception) -> Response:
        if isinstance(error, HTTPException):
            logger.warning(f"HTTP {error.code}: {error.description}")
        else:
            logger.error("", exc_info=True)
        return redirect(url_for(config.ENDPOINT_ERROR))

    wrap.__name__ = f.__name__
    return wrap


def handle_backend_error(f: Callable) -> Callable[[Exception], Response]:
    """Decorator to handle backend errors."""

    def wrap(error: Exception) -> Response:
        code: int
        message: str | ApiText
        if isinstance(error, IntegrityError):
            code = 409
            message = ApiText.HTTP_409
        elif isinstance(error, WebError):
            code = getattr(error, "code", 500)
            translation_key = getattr(error, "translation_key", None)
            if isinstance(translation_key, str):
                message = _(translation_key)
            else:
                message = ApiText.HTTP_500
        else:
            if request.is_json:
                info = f"Backend error with data: {str(request.get_json())}"
            else:
                info = ""
            logger.error(info, exc_info=True)
            code, message = 500, ApiText.HTTP_500
        return response(code, message)

    wrap.__name__ = f.__name__
    return wrap
