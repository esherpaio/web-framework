import re
import uuid
from enum import StrEnum

from flask import url_for
from flask_login import current_user
from werkzeug import Response
from werkzeug.security import generate_password_hash

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.resource.user import get_resource
from web.database.client import conn
from web.database.model import User, UserRoleId, Verification
from web.helper.api import ApiText, args_get, json_get, response
from web.i18n.base import _
from web.mail.routes.user import send_new_password, send_verification_url


class _Text(StrEnum):
    ACTIVATION_CHECK = _("API_USER_ACTIVATION_CHECK")
    ACTIVATION_SUCCESS = _("API_USER_ACTIVATION_SUCCESS")
    EMAIL_IN_USE = _("API_USER_EMAIL_IN_USE")
    EMAIL_INVALID = _("API_USER_EMAIL_INVALID")
    EMAIL_NOT_FOUND = _("API_USER_EMAIL_NOT_FOUND")
    PASSWORD_LENGTH = _("API_USER_PASSWORD_LENGTH")
    PASSWORD_NO_MATCH = _("API_USER_PASSWORD_NO_MATCH")
    PASSWORD_REQUEST_SEND = _("API_USER_PASSWORD_REQUEST_SEND")
    PASSWORD_RESET_SUCCESS = _("API_USER_PASSWORD_RESET_SUCCESS")
    REGISTER_SUCCESS = _("API_USER_REGISTER_SUCCESS")
    UPDATE_SUCCESS = _("API_USER_UPDATE_SUCCESS")
    VERIFICATION_FAILED = _("API_USER_VERIFICATION_FAILED")


@api_v1_bp.post("/users")
def post_users() -> Response:
    email, _ = json_get("email", str, nullable=False, lower_str=True)
    password_eval, _ = json_get("password_eval", str, nullable=False)
    password, _ = json_get("password", str, nullable=False)
    billing_id, _ = json_get("billing_id", int)
    shipping_id, _ = json_get("shipping_id", int)
    attributes, _ = json_get("attributes", dict, default={})

    # Validate email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return response(400, _Text.EMAIL_INVALID)

    # Validate password
    if len(password) < 8:
        return response(400, _Text.PASSWORD_LENGTH)
    if password != password_eval:
        return response(400, _Text.PASSWORD_NO_MATCH)

    with conn.begin() as s:
        # Validate email
        user = s.query(User).filter(User.email == email).first()
        if user:
            return response(409, _Text.EMAIL_IN_USE)

        # Insert user
        password_hash = generate_password_hash(password, method="pbkdf2:sha256:1000000")
        user = User(
            attributes=attributes,
            email=email,
            password_hash=password_hash,
            billing_id=billing_id,
            shipping_id=shipping_id,
            role_id=UserRoleId.USER,
        )
        s.add(user)

    resource = get_resource(user.id)
    return response(message=_Text.REGISTER_SUCCESS, data=resource)


@api_v1_bp.get("/users")
def get_users() -> Response:
    email, _ = args_get("email", str, nullable=False, lower_str=True)

    with conn.begin() as s:
        # Get user
        user = s.query(User).filter(User.email == email).first()
        if user is None:
            return response(404, _Text.EMAIL_NOT_FOUND)

    resource = [get_resource(user.id)]
    return response(data=resource)


@api_v1_bp.patch("/users/<int:user_id>")
def patch_users_id(user_id: int) -> Response:
    billing_id, has_billing_id = json_get("billing_id", int)
    shipping_id, has_shipping_id = json_get("shipping_id", int)

    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Check user
        if current_user.id != user_id:
            return response(401, ApiText.HTTP_401)

        # Update user
        if has_shipping_id:
            user.shipping_id = shipping_id
        if has_billing_id:
            user.billing_id = billing_id

    resource = get_resource(user.id)
    return response(message=_Text.UPDATE_SUCCESS, data=resource)


@api_v1_bp.post("/users/<int:user_id>/activation")
def post_users_id_activation(user_id: int) -> Response:
    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Insert verification
        verification_key = str(uuid.uuid4())
        verification = Verification(user_id=user.id, key=verification_key)
        s.add(verification)
        s.flush()

        # Send email
        verification_url = url_for(
            config.ENDPOINT_LOGIN,
            verification_key=verification.key,
            _external=True,
        )
        send_verification_url(email=user.email, verification_url=verification_url)

    return response(200, message=_Text.ACTIVATION_CHECK)


@api_v1_bp.patch("/users/<int:user_id>/activation")
def patch_users_id_activation(user_id: int) -> Response:
    verification_key, _ = json_get("verification_key", str)

    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Check verification
        verification = s.query(Verification).filter_by(key=verification_key).first()
        if verification is None:
            return response(401, _Text.VERIFICATION_FAILED)
        if not verification.is_valid:
            return response(401, _Text.VERIFICATION_FAILED)
        if verification.user_id != user_id:
            return response(401, _Text.VERIFICATION_FAILED)

        # Update activation
        user.is_active = True
        s.delete(verification)

    return response(200, message=_Text.ACTIVATION_SUCCESS)


@api_v1_bp.post("/users/<int:user_id>/password")
def post_users_id_password(user_id: int) -> Response:
    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Insert verification
        verification_key = str(uuid.uuid4())
        verification = Verification(user_id=user.id, key=verification_key)
        s.add(verification)
        s.flush()

        # Send email
        reset_url = url_for(
            "auth.password_reset",
            verification_key=verification_key,
            _external=True,
        )
        send_new_password(email=user.email, reset_url=reset_url)

    return response(200, _Text.PASSWORD_REQUEST_SEND)


@api_v1_bp.patch("/users/<int:user_id>/password")
def patch_users_id_password(user_id: int) -> Response:
    password, _ = json_get("password", str)
    password_eval, _ = json_get("password_eval", str)
    verification_key, _ = json_get("verification_key", str)

    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()
        if not user:
            return response(404, ApiText.HTTP_404)

        # Check verification
        verification = s.query(Verification).filter_by(key=verification_key).first()
        if verification is None:
            return response(401, _Text.VERIFICATION_FAILED)
        if not verification.is_valid:
            return response(401, _Text.VERIFICATION_FAILED)
        if verification.user_id != user_id:
            return response(401, _Text.VERIFICATION_FAILED)

        # Check password
        if len(password) < 8:
            return response(400, _Text.PASSWORD_LENGTH)
        if password != password_eval:
            return response(400, _Text.PASSWORD_NO_MATCH)

        # Update password
        password_hash = generate_password_hash(password, method="pbkdf2:sha256:1000000")
        user.password_hash = password_hash
        s.delete(verification)

    return response(200, _Text.PASSWORD_RESET_SUCCESS)
