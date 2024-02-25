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
from web.database import conn
from web.database.model import User, UserRoleId
from web.i18n import _
from web.libs.api import response

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
        User.email,
        User.billing_id,
        User.shipping_id,
        User.allow_mass_email,
        "password",
        "password_eval",
    }
    patch_columns = {
        User.billing_id,
        User.shipping_id,
        User.allow_mass_email,
    }
    get_filters = {
        User.email,
    }
    get_columns = {
        User.id,
        User.is_active,
        User.role_id,
        User.email,
        User.billing_id,
        User.shipping_id,
        User.allow_mass_email,
    }


#
# Endpoints
#


@api_v1_bp.post("/users")
def post_users() -> Response:
    api = UserAPI()
    data = api.gen_request_data(api.post_columns)
    with conn.begin() as s:
        model = api.model()
        set_password(s, data, model)
        val_email(s, data, model)
        set_role(s, data, model)
        api.insert(s, data, model)
        resource = api.gen_resource(s, model)
    return response(message=Text.USER_CREATED, data=resource)


@api_v1_bp.get("/users")
def get_users() -> Response:
    api = UserAPI()
    data = api.gen_query_data(api.get_filters)
    with conn.begin() as s:
        filters = api.gen_query_filters(data, required=True)
        models: list[User] = api.list_(s, *filters, limit=1)
        resources = api.gen_resources(s, models)
    return response(data=resources)


@api_v1_bp.get("/users/<int:user_id>")
def get_users_id(user_id: int) -> Response:
    api = UserAPI()
    with conn.begin() as s:
        filters = {User.id == current_user.id, User.is_active == true()}
        model: User = api.get(s, user_id, *filters)
        resource = api.gen_resource(s, model)
    return response(data=resource)


@api_v1_bp.patch("/users/<int:user_id>")
def patch_users_id(user_id: int) -> Response:
    api = UserAPI()
    data = api.gen_request_data(api.patch_columns)
    with conn.begin() as s:
        filters = {User.id == current_user.id, User.is_active == true()}
        model: User = api.get(s, user_id, *filters)
        api.update(s, data, model)
        resource = api.gen_resource(s, model)
    return response(message=Text.USER_UPDATED, data=resource)


#
# Functions
#


def set_password(s: Session, data: dict, model: User) -> None:
    password = data["password"]
    password_eval = data["password_eval"]
    if len(password) < 8:
        abort(response(400, Text.PASSWORD_LENGTH))
    if password != password_eval:
        abort(response(400, Text.PASSWORD_NO_MATCH))
    password_hash = generate_password_hash(password, "pbkdf2:sha256:1000000")
    model.password_hash = password_hash


def val_email(s: Session, data: dict, model: User) -> None:
    email = data["email"]
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        abort(response(400, Text.EMAIL_INVALID))
    user = s.query(User).filter(User.email == email.lower()).first()
    if user is not None:
        abort(response(409, Text.EMAIL_IN_USE))


def set_role(s: Session, data: dict, model: User) -> None:
    model.role_id = UserRoleId.USER
