import re
from enum import StrEnum

from flask import abort
from flask_login import current_user
from sqlalchemy import true
from sqlalchemy.orm.session import Session
from werkzeug import Response
from werkzeug.security import generate_password_hash

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1._base import API
from web.database.model import User
from web.database.model.user_role import UserRoleId, UserRoleLevel
from web.helper.api import json_get, response
from web.helper.user import access_control
from web.i18n.base import _


class _Text(StrEnum):
    EMAIL_IN_USE = _("API_USER_EMAIL_IN_USE")
    EMAIL_INVALID = _("API_USER_EMAIL_INVALID")
    PASSWORD_LENGTH = _("API_USER_PASSWORD_LENGTH")
    PASSWORD_NO_MATCH = _("API_USER_PASSWORD_NO_MATCH")
    REGISTER_SUCCESS = _("API_USER_REGISTER_SUCCESS")
    UPDATE_SUCCESS = _("API_USER_UPDATE_SUCCESS")


class UserAPI(API):
    model = User
    post_columns = {
        User.email,
        User.billing_id,
        User.shipping_id,
        User.attributes,
    }
    post_message = _Text.REGISTER_SUCCESS
    patch_columns = {
        User.billing_id,
        User.shipping_id,
    }
    patch_message = _Text.UPDATE_SUCCESS
    get_args = {
        User.email,
    }
    get_args_required = {
        User.email,
    }
    get_columns = {
        User.id,
        User.email,
        User.billing_id,
        User.shipping_id,
        User.attributes,
        User.role_id,
        User.is_active,
    }


@api_v1_bp.post("/users")
def post_users() -> Response:
    def validate(s: Session, user: User, data: dict) -> None:
        # Parse data
        email = data["email"]
        password = data["password"]
        password_eval = data["password_eval"]
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            abort(response(400, _Text.EMAIL_INVALID))
        user = s.query(User).filter(User.email == email.lower()).first()
        if user:
            abort(response(409, _Text.EMAIL_IN_USE))
        # Validate password
        if len(password) < 8:
            abort(response(400, _Text.PASSWORD_LENGTH))
        if password != password_eval:
            abort(response(400, _Text.PASSWORD_NO_MATCH))

    def set_data(s: Session, user: User, data: dict) -> None:
        password = data["password"]
        password_hash = generate_password_hash(password, "pbkdf2:sha256:1000000")
        data["password_hash"] = password_hash

    api = UserAPI()
    password, _ = json_get("password", str, nullable=False)
    password_eval, _ = json_get("password_eval", str, nullable=False)
    return api.post(
        add_request={
            "password": password,
            "password_eval": password_eval,
            "role_id": UserRoleId.USER,
        },
        pre_calls=[validate, set_data],
    )


@api_v1_bp.get("/users")
def get_users() -> Response:
    api = UserAPI()
    return api.get(as_list=True, max_size=1)


@access_control(UserRoleLevel.USER)
@api_v1_bp.patch("/users/<int:user_id>")
def patch_users_id(user_id: int) -> Response:
    api = UserAPI()
    return api.patch(
        user_id,
        filters={
            User.id == current_user.id,
            User.is_active == true(),
        },
    )
