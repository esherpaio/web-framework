from enum import StrEnum

from flask import Response

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Category, UserRoleLevel
from web.helper.api import ApiText, authorize, json_get, response
from web.helper.validation import gen_slug
from web.i18n.base import _


class _Text(StrEnum):
    REBOOT_REQUIRED = _("API_CATEGORY_REBOOT_REQUIRED")


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/categories")
def post_categories() -> Response:
    name, _ = json_get("name", str, nullable=False)
    order, _ = json_get("order", int)

    with conn.begin() as s:
        # Get category
        # Raise if category exists
        category = s.query(Category).filter_by(slug=gen_slug(name)).first()
        if category:
            if category.is_deleted:
                category.is_deleted = False
            else:
                return response(409, ApiText.HTTP_409)

        else:
            # Insert category
            category = Category(name=name, order=order)
            s.add(category)

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/categories/<int:category_id>")
def patch_categories_id(category_id: int) -> Response:
    child_id, has_child_id = json_get("child_id", int)
    in_header, has_in_header = json_get("in_header", bool)
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get category
        # Raise if category doesn't exist
        category = s.query(Category).filter_by(id=category_id, is_deleted=False).first()
        if not category:
            return response(404, ApiText.HTTP_404)

        # Update category
        if has_child_id:
            category.child_id = child_id
        if has_in_header:
            category.in_header = in_header
        if has_order:
            category.order_ = order

    return response(message=_Text.REBOOT_REQUIRED)


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/categories/<int:category_id>")
def delete_categories_id(category_id: int) -> Response:
    with conn.begin() as s:
        # Get category
        # Raise if category doesn't exist
        category = s.query(Category).filter_by(id=category_id, is_deleted=False).first()
        if not category:
            return response(404, ApiText.HTTP_404)

        # Delete category
        category.is_deleted = True

    return response(message=_Text.REBOOT_REQUIRED)
