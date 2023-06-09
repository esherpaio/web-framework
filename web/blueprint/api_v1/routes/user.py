import re
import uuid
from enum import StrEnum

from flask import Response, request, url_for
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from web import config
from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import User, UserVerification
from web.helper.api import ApiText, json_get, response
from web.helper.security import get_access
from web.mail.routes.user import send_new_password, send_verification_url


class _Text(StrEnum):
    # Todo: add translations
    PASSWORD_LENGTH = "Please enter at least 8 password characters."
    PASSWORD_NO_MATCH = "The passwords do not match."
    EMAIL_INVALID = "Please enter a valid email address."
    EMAIL_IN_USE = "This email address is already in use."
    EMAIL_NO_MATCH = "The email addresses do not match."
    REGISTER_SUCCESS = "Your account has been registered. Activate it with the URL in your email."  # noqa: E501
    ACTIVATION_SUCCESS = "Your account has been activated."
    VERIFY_FAILED = "We are unable to verify your account."
    PASSWORD_REQUEST_SEND = "Please follow the URL sent to your email."
    PASSWORD_RESET_SUCCESS = "Your password has been recovered."
    UPDATE_SUCCESS = "Your account has been updated."


@api_v1_bp.post("/users")
def post_users() -> Response:
    email, _ = json_get("email", str, nullable=False)
    password, _ = json_get("password", str, nullable=False)
    password_eval, _ = json_get("password_eval", str, nullable=False)

    # Validate password
    if len(password) < 8:
        return response(400, _Text.PASSWORD_LENGTH)
    if password != password_eval:
        return response(400, _Text.PASSWORD_NO_MATCH)

    # Validate email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return response(400, _Text.EMAIL_INVALID)

    # Generate password_hash and verification_key
    password_hash = generate_password_hash(password, method="pbkdf2:sha256:1000000")
    verification_key = str(uuid.uuid4())

    with conn.begin() as s:
        # Get user
        # Raise if it exists
        user = s.query(User).filter(func.lower(User.email) == func.lower(email)).first()
        if user:
            return response(409, _Text.EMAIL_IN_USE)

        # Insert user
        user = User(email=email, password_hash=password_hash)
        s.add(user)
        s.flush()

        # Insert verification
        user_verification = UserVerification(user_id=user.id, key=verification_key)
        s.add(user_verification)
        s.flush()

    # Create verification_url
    # Send email
    verification_url = url_for(
        config.ENDPOINT_LOGIN,
        verification_key=user_verification.key,
        _external=True,
    )
    send_verification_url(
        to=email,
        verification_url=verification_url,
    )

    return response(message=_Text.REGISTER_SUCCESS)


@api_v1_bp.get("/users")
def get_users() -> Response:
    email = request.args.get("email", type=str)
    has_email = "email" in request.args
    verification_key = request.args.get("verification_key", type=str)
    has_verification_key = "verification_key" in request.args

    with conn.begin() as s:
        # Get user_id by verification_key
        # Raise if verification doesn't exist
        if has_verification_key:
            verification = (
                s.query(UserVerification).filter_by(key=verification_key).first()
            )
            if verification is None:
                return response(404, ApiText.HTTP_404)
            data = {"id": verification.user_id}
            return response(data=data)

        # Get user_id by email
        # Raise if user doesn't exist
        if has_email:
            user = (
                s.query(User)
                .filter(func.lower(User.email) == func.lower(email))
                .first()
            )
            if user is None:
                return response(404, ApiText.HTTP_404)
            data = {"id": user.id}
            return response(data=data)

    return response(400, message=ApiText.HTTP_400)


@api_v1_bp.patch("/users/<int:user_id>")
def patch_users_id(user_id: int) -> Response:
    billing_id, has_billing_id = json_get("billing_id", int)
    is_active, has_is_active = json_get("is_active", bool)
    password, has_password = json_get("password", str)
    password_eval, has_password_eval = json_get("password_eval", str)
    shipping_id, has_shipping_id = json_get("shipping_id", int)
    verification_key, has_verification_key = json_get("verification_key", str)

    with conn.begin() as s:
        # Get user
        user = s.query(User).filter_by(id=user_id).first()

        # Flow for request password
        # Generate and insert verification_key
        # Send email
        if has_password and not has_password_eval and not has_verification_key:
            verification_key = str(uuid.uuid4())
            verification = UserVerification(user_id=user.id, key=verification_key)
            s.add(verification)
            s.flush()
            reset_url = url_for(
                "auth.password_reset",
                verification_key=verification.key,
                _external=True,
            )
            send_new_password(to=user.email, reset_url=reset_url)
            return response(200, _Text.PASSWORD_REQUEST_SEND)

        # Authorize request with verification_key
        # Raise if verification doesn't exist
        # Raise if user_id doesn't match
        if has_verification_key:
            verification = (
                s.query(UserVerification).filter_by(key=verification_key).first()
            )
            if verification is None:
                return response(401, _Text.VERIFY_FAILED)
            if verification.user_id != user_id:
                return response(401, _Text.VERIFY_FAILED)

        # Authorize request with access
        # Raise if user_id doesn't match
        else:
            access = get_access(s)
            if access.user_id != user_id:
                return response(401, _Text.VERIFY_FAILED)

        # Update is_active
        if has_is_active and has_verification_key:
            user.is_active = is_active
            return response(200, _Text.ACTIVATION_SUCCESS)

        # Update password
        if has_password and has_password_eval and has_verification_key:
            if len(password) < 8:
                return response(400, _Text.PASSWORD_LENGTH)
            if password != password_eval:
                return response(400, _Text.PASSWORD_NO_MATCH)
            password_hash = generate_password_hash(
                password, method="pbkdf2:sha256:1000000"
            )
            user.password_hash = password_hash
            return response(200, _Text.PASSWORD_RESET_SUCCESS)

        # Update shipping_id
        if has_shipping_id:
            user.shipping_id = shipping_id

        # Update billing_id
        if has_billing_id:
            user.billing_id = billing_id

    return response(message=_Text.UPDATE_SUCCESS)
