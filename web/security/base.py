import uuid
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from json import JSONEncoder
from typing import Any, Literal

import jwt
from flask import Flask, current_app, g, request
from werkzeug import Response

from web.api.utils import ApiText, response
from web.config import config
from web.database import conn
from web.database.model import User, UserRoleLevel
from web.libs.logger import log

from .enum import G
from .error import CSRFError, Forbidden, JWTError, NoAuthorizationError, SecurityError
from .user import current_user

#
# Constants
#

CSRF_ENABLED = False
CSRF_COOKIE_NAME = "csrf_token"
CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

KEY_HEADER_NAME = "Authorization"

JWT_SECRET = "secret"
JWT_ISSUER = "https://esherpa.io/"
JWT_AUDIENCE = "https://esherpa.io/"

JWT_COOKIE_DOMAIN = "esherpa.io"
JWT_COOKIE_NAME = "access_token"
JWT_COOKIE_MAX_AGE = 300

JWT_ENCODE_ALGORITHM = "HS256"
JWT_DECODE_ALGORITHMS = ["HS256"]
JWT_DECODE_LEEWAY_S = 60


#
# Base
#


class Security:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.app.register_error_handler(SecurityError, self.on_error)
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)

    @staticmethod
    def on_error(error: SecurityError) -> Response:
        log.warning(f"JWT error: {error}")
        if isinstance(error, Forbidden):
            code, message = 403, ApiText.HTTP_403
        else:
            code, message = 401, ApiText.HTTP_401
        return response(code, message)

    def before_request(self) -> None:
        user_id = None
        if KEY_HEADER_NAME in request.headers:
            user_id = header_authentication()
        if JWT_COOKIE_NAME in request.cookies:
            user_id = cookie_authentication()
        g._user_id = user_id

    def after_request(self, response: Response) -> Response:
        if JWT_COOKIE_NAME in request.cookies and G.USER_ID in g:
            access_token = encode_jwt(g._user_id, expires_delta=False)
            set_jwt(response, access_token)
        return response


def secure(level: UserRoleLevel | None = None) -> Any:
    def decorate(f):
        def wrap(*args, **kwargs):
            if (
                current_user is None
                or not current_user.is_active
                or current_user.role.level < level
            ):
                raise Forbidden
            return current_app.ensure_sync(f)(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


#
# Key authentication
#


def header_authentication() -> int:
    auth = request.headers.get("Authorization")
    if auth is None:
        raise NoAuthorizationError
    api_key = auth.replace("Bearer ", "", 1)
    with conn.begin() as s:
        user = s.query(User).filter_by(api_key=api_key, is_active=True).first()
    if user is None:
        raise JWTError
    return user.id


#
# JWT authentication
#


def cookie_authentication() -> int:
    encoded_token, csrf_token = get_jwt()
    token = decode_jwt(encoded_token, csrf_token)
    return token["sub"]


def get_jwt() -> tuple[str, str | None]:
    encoded_token = request.cookies.get(JWT_COOKIE_NAME)
    if encoded_token is None:
        raise NoAuthorizationError

    if request.method in CSRF_METHODS:
        csrf_value = request.cookies.get(CSRF_COOKIE_NAME)
        if csrf_value is None:
            raise CSRFError
    else:
        csrf_value = None

    return encoded_token, csrf_value


def encode_jwt(identity: int, expires_delta: timedelta | Literal[False]) -> str:
    now = datetime.now(timezone.utc)
    token_data = {
        # registered claims
        # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
        "iss": JWT_ISSUER,
        "sub": identity,
        "aud": JWT_AUDIENCE,
        "nbf": now,
        "iat": now,
        "jti": str(uuid.uuid4()),
        # custom claims
        "csrf": str(uuid.uuid4()),
    }
    if expires_delta:
        token_data["exp"] = now + expires_delta
    return jwt.encode(
        token_data,
        JWT_SECRET,
        algorithm=JWT_ENCODE_ALGORITHM,
        json_encoder=JSONEncoder,
    )


def decode_jwt(encoded_token: str, csrf_value=None) -> dict:
    try:
        decoded_token = jwt.decode(
            encoded_token,
            JWT_SECRET,
            algorithms=JWT_DECODE_ALGORITHMS,
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            leeway=timedelta(seconds=JWT_DECODE_LEEWAY_S),
        )
    except Exception:
        raise JWTError

    if csrf_value:
        if "csrf" not in decoded_token:
            raise JWTError
        if not compare_digest(decoded_token["csrf"], csrf_value):
            raise CSRFError

    return decoded_token


def set_jwt(response: Response, access_token: str, max_age=None, domain=None) -> None:
    if not config.APP_DEBUG:
        secure = True
        domain = JWT_COOKIE_DOMAIN
    else:
        secure = False
        domain = None

    response.set_cookie(
        JWT_COOKIE_NAME,
        value=access_token,
        max_age=JWT_COOKIE_MAX_AGE,
        secure=secure,
        httponly=True,
        domain=domain,
        path=None,
        samesite=None,
    )

    if CSRF_ENABLED:
        csrf_token = decode_jwt(access_token)["csrf"]
        response.set_cookie(
            CSRF_COOKIE_NAME,
            value=csrf_token,
            max_age=max_age or config.cookie_max_age,
            secure=config.cookie_secure,
            httponly=False,
            domain=domain or config.cookie_domain,
            path=None,
            samesite=None,
        )
