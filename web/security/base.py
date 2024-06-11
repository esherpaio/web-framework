import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hmac import compare_digest
from json import JSONEncoder
from typing import Any, Literal

import jwt
from flask import Flask, Response, current_app, g, has_request_context, request, url_for
from sqlalchemy.orm import joinedload
from werkzeug.local import LocalProxy

from web.api.utils import ApiText, response
from web.config import config
from web.database import conn
from web.database.model import User, UserRoleLevel
from web.libs.logger import log

#
# Constants
#

JWT_SECRET = "secret"

CSRF_ENABLED = False
CSRF_HEADER_NAME = "X-CSRF-TOKEN"
CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
CSRF_COOKIE_NAME = "csrf_token"

JWT_COOKIE_DOMAIN = "esherpa.io"
JWT_COOKIE_MAX_AGE = 31540000
JWT_COOKIE_NAME = "access_token"

JWT_ENCODE_ALGORITHM = "HS256"
JWT_ENCODE_ISSUER = "https://esherpa.io/"
JWT_ENCODE_AUDIENCE = "https://esherpa.io/"

JWT_DECODE_ALGORITHMS = ["HS256"]
JWT_DECODE_ISSUER = "https://esherpa.io/"
JWT_DECODE_AUDIENCE = "https://esherpa.io/"
JWT_DECODE_LEEWAY_S = 60


#
# Exceptions
#


class SecurityError(Exception):
    pass


class JWTError(SecurityError):
    pass


class CSRFError(SecurityError):
    pass


class NoAuthorizationError(SecurityError):
    pass


class Forbidden(SecurityError):
    pass


#
# Enums
#


class LocationType(StrEnum):
    HEADER = "header"
    COOKIE = "cookie"


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
        log.info(f"JWT error: {error}")
        if isinstance(error, Forbidden):
            code, message = 403, ApiText.HTTP_403
        else:
            code, message = 401, ApiText.HTTP_401
        links = {"login": url_for(config.ENDPOINT_LOGIN)}
        return response(code, message, links=links)

    @staticmethod
    def get_user_id(locations: list[LocationType] | None) -> int | None:
        if locations is None:
            locations = []
        user_id = None
        for location in locations:
            if location == LocationType.HEADER:
                user_id = authenticate_header()
            if location == LocationType.COOKIE:
                user_id = authenticate_cookie()
            if user_id is not None:
                break
        return user_id

    def before_request(self) -> None:
        try:
            user_id = self.get_user_id(
                locations=[LocationType.HEADER, LocationType.COOKIE]
            )
        except NoAuthorizationError:
            user_id = None
        g._user_id = user_id

    @staticmethod
    def after_request(response: Response) -> Response:
        if "_user_id" in g:
            access_token = encode_jwt(g._user_id, expires_delta=False)
            set_jwt(response, access_token)
        return response


def authorize(level: UserRoleLevel | None = None, redirect_: bool = False) -> Any:
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
# Header authorization
#


def authenticate_header() -> int:
    api_key = get_api_key()
    user = decode_api_key(api_key)
    return user.id


def get_api_key() -> str:
    auth = request.headers.get("Authorization")
    if auth is None:
        raise NoAuthorizationError
    return auth.replace("Bearer ", "", 1)


def decode_api_key(api_key: str) -> User:
    with conn.begin() as s:
        user = s.query(User).filter_by(api_key=api_key, is_active=True).first()
        if user is None:
            raise JWTError
    return user


#
# Cookie authorization
#


def authenticate_cookie() -> int:
    encoded_token, csrf_token = get_encoded_jwt()
    token = decode_jwt(encoded_token, csrf_token)
    return token["sub"]


def encode_jwt(identity: int, expires_delta: timedelta | Literal[False]) -> str:
    now = datetime.now(timezone.utc)
    token_data = {
        # registered claims
        # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
        "iss": JWT_ENCODE_ISSUER,
        "sub": identity,
        "aud": JWT_ENCODE_AUDIENCE,
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


def get_encoded_jwt() -> tuple[str, str | None]:
    encoded_token = request.cookies.get(JWT_COOKIE_NAME)
    if not encoded_token:
        raise NoAuthorizationError('Missing cookie "{}"'.format(JWT_COOKIE_NAME))

    if request.method in CSRF_METHODS:
        csrf_value = request.headers.get(CSRF_HEADER_NAME, None)
        if not csrf_value:
            raise CSRFError("Missing CSRF token")
    else:
        csrf_value = None

    return encoded_token, csrf_value


def decode_jwt(encoded_token: str, csrf_value=None) -> dict:
    try:
        decoded_token = jwt.decode(
            encoded_token,
            JWT_SECRET,
            algorithms=JWT_DECODE_ALGORITHMS,
            audience=JWT_DECODE_AUDIENCE,
            issuer=JWT_DECODE_ISSUER,
            leeway=timedelta(seconds=JWT_DECODE_LEEWAY_S),
        )
    except Exception:
        raise JWTError

    if csrf_value:
        if "csrf" not in decoded_token:
            raise JWTError("Missing claim: csrf")
        if not compare_digest(decoded_token["csrf"], csrf_value):
            raise CSRFError("CSRF double submit tokens do not match")

    return decoded_token


def set_jwt(response: Response, access_token: str, max_age=None, domain=None) -> None:
    if not config.APP_DEVELOP:
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


#
# Proxy
#


def _get_proxy_user() -> User | None:
    if has_request_context():
        if "_user" in g:
            return g._user
        if "_user" not in g and "_user_id" in g:
            with conn.begin() as s:
                user = (
                    s.query(User)
                    .options(joinedload(User.role))
                    .filter_by(id=g._user_id, is_active=True)
                    .first()
                )
            if user is not None:
                g._user = user
        return g._user


current_user: Any = LocalProxy(lambda: _get_proxy_user())
