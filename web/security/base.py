import time
import uuid
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from json import JSONEncoder
from random import randint
from typing import Any, Literal

import jwt
from flask import Flask, current_app, g, redirect, request, url_for
from sqlalchemy.orm import joinedload
from werkzeug import Response

from web.api.utils import json_response
from web.config import config
from web.database import conn
from web.database.model import User, UserRoleId, UserRoleLevel
from web.libs.logger import log

from .enum import AuthType
from .error import AuthError, CSRFError, Forbidden, JWTError, KEYError, NoValueError
from .user import current_user

#
# Constants
#

CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
CSRF_COOKIE_NAME = "csrf_token"
CSRF_COOKIE_MAX_AGE = 31540000

KEY_HEADER_NAME = "Authorization"

JWT_SECRET = "secret"
JWT_ISSUER = "https://esherpa.io/"
JWT_AUDIENCE = "https://esherpa.io/"

JWT_COOKIE_DOMAIN = "esherpa.io"
JWT_COOKIE_NAME = "access_token"
JWT_COOKIE_MAX_AGE = 31540000

JWT_ENCODE_ALGORITHM = "HS256"
JWT_DECODE_ALGORITHMS = ["HS256"]
JWT_DECODE_LEEWAY_S = 60


#
# Base
#


class Security:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.app.register_error_handler(AuthError, self.on_error)
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)

    @staticmethod
    def on_error(error: AuthError) -> Response:
        log.debug(f"AuthError {type(error).__name__}")
        if request.blueprint is not None and (
            request.blueprint.startswith("api")
            or request.blueprint.startswith("webhook")
        ):
            response = json_response(error.code, error.message)
        else:
            response = redirect(url_for(config.ENDPOINT_LOGIN))
        if error.code == 401:
            del_jwt(response)
        return response

    def create_guest(self) -> int:
        with conn.begin() as s:
            user = User(is_active=True, role_id=UserRoleId.GUEST)
            s.add(user)
        return user.id

    def before_request(self) -> None:
        user_id = None
        if KEY_HEADER_NAME in request.headers:
            user_id = key_authentication()
            g._user_auth = AuthType.KEY
        elif JWT_COOKIE_NAME in request.cookies:
            user_id = jwt_authentication()
            g._user_auth = AuthType.JWT
        else:
            user_id = self.create_guest()
            g._user_auth = AuthType.JWT
        g._user_id = user_id

    def after_request(self, response: Response) -> Response:
        auth_type = getattr(g, "_user_auth", None)
        if auth_type == AuthType.NONE:
            del_jwt(response)
        elif auth_type == AuthType.JWT:
            access_token, csrf_token = encode_jwt(g._user_id, expires_delta=False)
            set_jwt(response, access_token, csrf_token)
        return response


def secure(level: UserRoleLevel | None = None) -> Any:
    def decorate(f):
        def wrap(*args, **kwargs):
            if (
                not current_user
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


def key_authentication() -> int:
    auth = request.headers.get("Authorization")
    if auth is None:
        raise NoValueError
    api_key = auth.replace("Bearer ", "", 1)
    with conn.begin() as s:
        user = (
            s.query(User)
            .options(joinedload(User.role))
            .filter_by(api_key=api_key, is_active=True)
            .first()
        )
    if user is None:
        raise KEYError
    if not compare_digest(user.api_key, api_key):
        raise KEYError
    return user.id


#
# JWT authentication
#


def jwt_authentication() -> int:
    encoded_token, csrf_token = get_jwt()
    token = decode_jwt(encoded_token, csrf_token)
    return token["sub"]


def get_jwt() -> tuple[str, str | None]:
    encoded_token = request.cookies.get(JWT_COOKIE_NAME)
    if encoded_token is None:
        raise NoValueError

    if request.method in CSRF_METHODS:
        csrf_value = request.cookies.get(CSRF_COOKIE_NAME)
        if csrf_value is None:
            raise NoValueError
    else:
        csrf_value = None

    return encoded_token, csrf_value


def encode_jwt(
    user_id: int, expires_delta: timedelta | Literal[False]
) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    csrf_token = str(uuid.uuid4())
    token_data = {
        # registered claims
        # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
        "iss": JWT_ISSUER,
        "sub": user_id,
        "aud": JWT_AUDIENCE,
        "nbf": now,
        "iat": now,
        "jti": str(uuid.uuid4()),
        # custom claims
        "csrf": csrf_token,
    }
    if expires_delta:
        token_data["exp"] = now + expires_delta
    return jwt.encode(
        token_data,
        JWT_SECRET,
        algorithm=JWT_ENCODE_ALGORITHM,
        json_encoder=JSONEncoder,
    ), csrf_token


def decode_jwt(encoded_token: str, csrf_token: str | None = None) -> dict:
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

    if csrf_token is not None:
        if "csrf" not in decoded_token:
            raise JWTError
        if not compare_digest(decoded_token["csrf"], csrf_token):
            raise CSRFError

    return decoded_token


def set_jwt(response: Response, access_token: str, csrf_token: str) -> None:
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
        path="/",
        samesite=None,
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=CSRF_COOKIE_MAX_AGE,
        secure=secure,
        httponly=False,
        domain=domain,
        path="/",
        samesite=None,
    )


def del_jwt(response: Response) -> None:
    response.delete_cookie(JWT_COOKIE_NAME)
    response.delete_cookie(CSRF_COOKIE_NAME)


def jwt_login(user_id: int) -> None:
    time.sleep(randint(0, 1000) / 1000)
    g._user = None
    g._user_id = user_id
    g._user_auth = AuthType.JWT


def jwt_logout() -> None:
    time.sleep(randint(0, 1000) / 1000)
    g._user = None
    g._user_id = None
    g._user_auth = AuthType.NONE
