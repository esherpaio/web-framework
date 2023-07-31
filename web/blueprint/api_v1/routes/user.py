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
from web.database.model.user_role import UserRoleId
from web.helper.api import json_get, response
from web.i18n.base import _

#
# Configuration
#


class Text(StrEnum):
    EMAIL_IN_USE = _("API_USER_EMAIL_IN_USE")
    EMAIL_INVALID = _("API_USER_EMAIL_INVALID")
    PASSWORD_LENGTH = _("API_USER_PASSWORD_LENGTH")
    PASSWORD_NO_MATCH = _("API_USER_PASSWORD_NO_MATCH")
    USER_CREATED = _("API_USER_REGISTER_SUCCESS")
    USER_UPDATED = _("API_USER_UPDATE_SUCCESS")


class UserAPI(API):
    model = User
    post_columns = {
        User.attributes,
        User.billing_id,
        User.email,
        User.shipping_id,
    }
    post_message = Text.USER_CREATED
    patch_columns = {
        User.billing_id,
        User.shipping_id,
    }
    patch_message = Text.USER_UPDATED
    get_args = {User.email}
    get_columns = {
        User.attributes,
        User.billing_id,
        User.email,
        User.id,
        User.is_active,
        User.role_id,
        User.shipping_id,
    }


def val_password(s: Session, data: dict, *args) -> None:
    password, _ = json_get("password", str, nullable=False)
    password_eval, _ = json_get("password_eval", str, nullable=False)
    if len(password) < 8:
        abort(response(400, Text.PASSWORD_LENGTH))
    if password != password_eval:
        abort(response(400, Text.PASSWORD_NO_MATCH))


def val_email(s: Session, data: dict, *args) -> None:
    email, _ = json_get("email", str, nullable=False)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        abort(response(400, Text.EMAIL_INVALID))
    user = s.query(User).filter(User.email == email.lower()).first()
    if user is not None:
        abort(response(409, Text.EMAIL_IN_USE))


def set_password(s: Session, data: dict, *args) -> None:
    password, _ = json_get("password", str, nullable=False)
    password_hash = generate_password_hash(password, "pbkdf2:sha256:1000000")
    data["password_hash"] = password_hash


def set_role_id(s: Session, data: dict, *args) -> None:
    data["role_id"] = UserRoleId.USER


#
# Endpoints
#


@api_v1_bp.post("/users")
def post_users() -> Response:
    api = UserAPI()
    return api.post(
        pre_calls=[val_password, val_email, set_password, set_role_id],
    )


@api_v1_bp.get("/users")
def get_users() -> Response:
    api = UserAPI()
    return api.get(
        as_list=True,
        max_size=1,
        args_required=True,
    )


@api_v1_bp.get("/users/<int:user_id>")
def get_users_id(user_id: int) -> Response:
    api = UserAPI()
    return api.get(
        user_id,
        filters={User.id == current_user.id, User.is_active == true()},
    )


@api_v1_bp.patch("/users/<int:user_id>")
def patch_users_id(user_id: int) -> Response:
    api = UserAPI()
    return api.patch(
        user_id,
        filters={User.id == current_user.id, User.is_active == true()},
    )
