import logging

import psycopg2.errors
import sqlalchemy.exc
from flask import redirect, request
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import Response
from werkzeug.exceptions import HTTPException

from web.api import HttpText, json_response
from web.app.urls import parse_url, url_for
from web.error import WebError
from web.i18n import _
from web.logger import log
from web.setup import settings
from web.utils.obfuscation import obfuscate_data


def handle_error(error: Exception) -> Response:
    """Handle errors."""
    if request.blueprint is not None and request.blueprint.startswith(
        ("api", "webhook")
    ):
        return handle_backend_error(error)
    return handle_frontend_error(error)


def handle_frontend_error(error: Exception) -> Response:
    """Handle frontend errors."""
    # Parse error information
    if isinstance(error, HTTPException):
        code = error.code
    elif isinstance(error, NoResultFound):
        code = 404
    else:
        code = None

    # Determine log level
    if code is None or code >= 500:
        level = logging.ERROR
    else:
        level = logging.WARNING

    # Log error and redirect
    info = ["Frontend error", f"{request.method} {request.full_path}"]
    exc_info = True if level >= logging.ERROR else False
    log.log(level, " | ".join(info), exc_info=exc_info)
    url = parse_url(settings.ENDPOINT_ERROR, _func=url_for)
    return redirect(url, code=302)


def handle_backend_error(error: Exception) -> Response:
    """Handle backend errors."""
    # Parse error information
    if isinstance(error, WebError):
        code = error.code
        if error.translation_key is not None:
            message = _(error.translation_key, **error.translation_kwargs)
        else:
            message = HttpText.HTTP_500
    elif isinstance(error, sqlalchemy.exc.IntegrityError):
        if isinstance(error.orig, psycopg2.errors.ForeignKeyViolation):
            code = 409
            message = HttpText.HTTP_409
        else:
            code = 500
            message = HttpText.HTTP_500
    else:
        code = 500
        message = HttpText.HTTP_500

    # Log error and return response
    info = [
        "Backend error",
        f"{request.method} {request.full_path}",
        f"message {message}",
    ]
    if request.is_json:
        data = obfuscate_data(request.get_json())
        info.append(f"data {data}")
    exc_info = code >= 500
    log.error(" | ".join(info), exc_info=exc_info)
    return json_response(code, message)
