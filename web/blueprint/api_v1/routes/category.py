from werkzeug import Response

from web.api.utils import ApiText, json_get, json_response
from web.auth import authorize
from web.blueprint.api_v1 import api_v1_bp
from web.database import conn
from web.database.model import Category, UserRoleLevel
from web.libs.parse import gen_slug

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/categories")
@authorize(UserRoleLevel.ADMIN)
def post_categories() -> Response:
    name, _ = json_get("name", str, nullable=False)
    order, _ = json_get("order", int)

    with conn.begin() as s:
        # Get or restore category
        category = s.query(Category).filter_by(slug=gen_slug(name)).first()
        if category:
            if category.is_deleted:
                category.is_deleted = False
                return json_response()
            else:
                return json_response(409, ApiText.HTTP_409)

        # Insert category
        category = Category(name=name, order=order)
        s.add(category)

    return json_response()


@api_v1_bp.patch("/categories/<int:category_id>")
@authorize(UserRoleLevel.ADMIN)
def patch_categories_id(category_id: int) -> Response:
    attributes, has_attributes = json_get("attributes", dict, default={})
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get category
        category = s.query(Category).filter_by(id=category_id, is_deleted=False).first()
        if not category:
            return json_response(404, ApiText.HTTP_404)

        # Update category
        if has_attributes:
            category.attributes = attributes
        if has_order:
            category.order = order

    return json_response()


@api_v1_bp.delete("/categories/<int:category_id>")
@authorize(UserRoleLevel.ADMIN)
def delete_categories_id(category_id: int) -> Response:
    with conn.begin() as s:
        # Delete category
        category = s.query(Category).filter_by(id=category_id, is_deleted=False).first()
        if not category:
            return json_response(404, ApiText.HTTP_404)
        category.is_deleted = True

    return json_response()


#
# Functions
#
