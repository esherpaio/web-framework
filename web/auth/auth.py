import uuid
from datetime import datetime, timedelta, timezone
from hmac import compare_digest
from json import JSONEncoder
from typing import Any, Literal, Type

import jwt
from flask import Flask, current_app, g, redirect, request
from sqlalchemy.orm import joinedload
from werkzeug import Response

from web.api import json_response
from web.app.urls import parse_url, url_for
from web.config import config
from web.database import conn
from web.database.model import User, UserRoleLevel
from web.logger import log

from .enum import AuthType, G
from .error import AuthError, CSRFError, Forbidden, JWTError, KEYError, NoValueError
from .proxy import current_user

#
# Constants
#

AUTH_KEY_HEADER_NAME = "Authorization"
AUTH_JWT_COOKIE_NAME = "access_token"
AUTH_JWT_ENCODE_ALGORITHM = "HS256"
AUTH_JWT_DECODE_ALGORITHMS = ["HS256"]
AUTH_CSRF_COOKIE_NAME = "csrf_token"
AUTH_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]


#
# Base
#


class Auth:
    def __init__(self, app: Flask | None = None) -> None:
        if app is not None:
            self.init(app)

    def init(self, app: Flask) -> None:
        app.register_error_handler(AuthError, self.on_error)
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self) -> None:
        if AUTH_KEY_HEADER_NAME in request.headers:
            user_id = key_authentication()
            auth_type = AuthType.KEY
        elif AUTH_JWT_COOKIE_NAME in request.cookies:
            user_id = jwt_authentication()
            auth_type = AuthType.JWT
        else:
            user_id = None
            auth_type = AuthType.NONE
        g._user_id = user_id
        g._auth_type = auth_type

    def after_request(self, response: Response) -> Response:
        auth_type = getattr(g, G.AUTH_TYPE, None)
        if auth_type == AuthType.NONE:
            del_jwt(response)
        user_id = g.get(G.USER_ID, None)
        if auth_type == AuthType.JWT and user_id is not None:
            access_token, csrf_token = encode_jwt(
                user_id,
                expires_delta=timedelta(seconds=config.AUTH_JWT_EXPIRES_S),
            )
            set_jwt(response, access_token, csrf_token)
        return response

    @staticmethod
    def on_error(error: Type[AuthError]) -> Response:
        user_id = getattr(g, G.USER_ID, None)
        log.debug(f"Auth error {error.name} at user {user_id}")
        if request.blueprint is not None and (
            request.blueprint.startswith(("api", "webhook"))
        ):
            response = json_response(error.code, error.message)
        else:
            url = parse_url(config.ENDPOINT_LOGIN, _func=url_for)
            response = redirect(url, code=302)
        if error.code == 401:
            del_jwt(response)
        return response


#
# Authorization
#


def authorize(level: UserRoleLevel | None = None) -> Any:
    def decorate(f):
        def wrap(*args, **kwargs):
            auth = authorize_user(level)
            if auth is not None:
                return auth
            return current_app.ensure_sync(f)(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


def authorize_user(level: UserRoleLevel | None = None) -> Response | None:
    if (
        not current_user
        or not current_user.is_active
        or current_user.role.level < level
    ):
        return Auth.on_error(Forbidden)
    return None


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
    encoded_token = request.cookies.get(AUTH_JWT_COOKIE_NAME)
    if encoded_token is None:
        raise NoValueError

    if request.method in AUTH_CSRF_METHODS:
        csrf_value = request.cookies.get(AUTH_CSRF_COOKIE_NAME)
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
        "sub": user_id,
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
        config.AUTH_JWT_SECRET,
        algorithm=AUTH_JWT_ENCODE_ALGORITHM,
        json_encoder=JSONEncoder,
    ), csrf_token


def decode_jwt(encoded_token: str, csrf_token: str | None = None) -> dict:
    try:
        decoded_token = jwt.decode(
            encoded_token,
            config.AUTH_JWT_SECRET,
            algorithms=AUTH_JWT_DECODE_ALGORITHMS,
            leeway=timedelta(seconds=config.AUTH_JWT_DECODE_LEEWAY_S),
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
    if config.APP_URL_SCHEME == "https":
        secure = True
    else:
        secure = False

    response.set_cookie(
        AUTH_JWT_COOKIE_NAME,
        value=access_token,
        max_age=config.AUTH_JWT_EXPIRES_S,
        secure=secure,
        httponly=True,
        domain=None,
        path="/",
        samesite=None,
    )
    response.set_cookie(
        AUTH_CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=config.AUTH_JWT_EXPIRES_S,
        secure=secure,
        httponly=False,
        domain=None,
        path="/",
        samesite=None,
    )


def del_jwt(response: Response) -> None:
    response.delete_cookie(AUTH_JWT_COOKIE_NAME)
    response.delete_cookie(AUTH_CSRF_COOKIE_NAME)
