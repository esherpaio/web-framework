import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hmac import compare_digest
from json import JSONEncoder
from typing import Any, Literal

import jwt
from flask import (
    Flask,
    Response,
    abort,
    current_app,
    g,
    has_request_context,
    redirect,
    request,
    url_for,
)
from werkzeug.local import LocalProxy

from web.api.utils import ApiText, response
from web.config import config
from web.database import conn
from web.database.model import User, UserRoleId, UserRoleLevel

#
# Constants
#

JWT_COOKIE_DOMAIN = "esherpa.io"
JWT_COOKIE_MAX_AGE = 31540000
JWT_EXPIRES_GUEST = False
JWT_EXPIRES_USER = 3600

JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-TOKEN"
JWT_ACCESS_CSRF_FIELD_NAME = "csrf_token"

JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"
JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-TOKEN"
JWT_REFRESH_CSRF_FIELD_NAME = "csrf_token"

JWT_SECRET = "secret"
JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

JWT_ENCODE_ALGORITHM = "HS256"
JWT_ENCODE_ISSUER = "https://esherpa.io/"
JWT_ENCODE_AUDIENCE = "https://esherpa.io/"

JWT_DECODE_ALGORITHMS = ["HS256"]
JWT_DECODE_ISSUER = "https://esherpa.io/"
JWT_DECODE_AUDIENCE = "https://esherpa.io/"
JWT_DECODE_LEEWAY_S = 0


#
# Exceptions
#


class JWTException(Exception):
    pass


class NoAuthorizationError(JWTException):
    pass


class CSRFError(JWTException):
    pass


class JWTDecodeError(JWTException):
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


class JWT:
    def __init__(self, app: Flask, blueprints: dict[str, dict | None]) -> None:
        self.app = app
        self.app.after_request(self.after_request)
        for name, bp in self.app.blueprints.items():
            if name in blueprints:
                kwargs = blueprints[name] or {}
                bp.before_request(lambda: check_access(**kwargs))

    @staticmethod
    def after_request(response):
        if "_user" in g:
            user = g._user
            access_token = encode_jwt(user.id, expires_delta=False)
            set_jwt(response, access_token)
        return response


def check_access(
    optional: bool = False,
    redirect_: bool = False,
    create: bool = False,
    locations: LocationType | None = None,
    level: UserRoleLevel | None = None,
) -> Any:
    def decorate(f):
        def wrap(*args, **kwargs):
            _check_access(
                optional=optional,
                redirect_=redirect_,
                create=create,
                locations=locations,
                level=level,
            )
            return current_app.ensure_sync(f)(*args, **kwargs)

        wrap.__name__ = f.__name__
        return wrap

    return decorate


def _check_access(
    optional: bool = False,
    redirect_: bool = False,
    create: bool = False,
    locations: LocationType | None = None,
    level: UserRoleLevel | None = None,
) -> None:
    if locations is None:
        locations = [LocationType.COOKIE]

    # Authenticate user
    try:
        user_id = None
        for location in locations:
            if location == LocationType.HEADER:
                user_id = authenticate_header()
            if location == LocationType.COOKIE:
                user_id = authenticate_cookie()
            if user_id is not None:
                break
    except Exception:
        if not optional:
            if redirect_:
                abort(redirect(url_for(config.ENDPOINT_LOGIN)))
            abort(response(401, ApiText.HTTP_401))

    # Create new user
    if create:
        with conn.begin() as s:
            user = User(is_active=True, role_id=UserRoleId.GUEST)
            s.add(user)
        g._user = user

    # Authorize user
    if level is not None:
        if (
            current_user is None
            or not current_user.is_active
            or current_user.role.level < level
        ):
            if redirect_:
                abort(redirect(url_for(config.ENDPOINT_LOGIN)))
            abort(response(403, ApiText.HTTP_403))


#
# Header authorization
#


def authenticate_header(self) -> int:
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
            raise JWTDecodeError
    return user


#
# Cookie authorization
#


def authenticate_cookie(self) -> int:
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


def get_encoded_jwt(refresh: bool) -> tuple[str, str | None]:
    if refresh:
        cookie_key = JWT_REFRESH_COOKIE_NAME
        csrf_header_key = JWT_REFRESH_CSRF_HEADER_NAME
    else:
        cookie_key = JWT_ACCESS_COOKIE_NAME
        csrf_header_key = JWT_ACCESS_CSRF_HEADER_NAME

    encoded_token = request.cookies.get(cookie_key)
    if not encoded_token:
        raise NoAuthorizationError('Missing cookie "{}"'.format(cookie_key))

    if request.method in JWT_CSRF_METHODS:
        csrf_value = request.headers.get(csrf_header_key, None)
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
        raise JWTDecodeError

    if csrf_value:
        if "csrf" not in decoded_token:
            raise JWTDecodeError("Missing claim: csrf")
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
        JWT_ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=JWT_COOKIE_MAX_AGE,
        secure=secure,
        httponly=True,
        domain=domain,
        path=None,
        samesite=None,
    )

    if config.cookie_csrf_protect and config.csrf_in_cookies:
        csrf_token = decode_jwt(access_token)["csrf"]
        response.set_cookie(
            config.access_csrf_cookie_name,
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
    return None


current_user: Any = LocalProxy(lambda: _get_proxy_user())
