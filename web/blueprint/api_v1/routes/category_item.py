from flask import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import CategoryItem, UserRoleLevel
from web.helper.api import response, ApiText, json_get
from web.helper.security import authorize


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/categories/<int:category_id>/items")
def post_categories_id_items(category_id: int) -> Response:
    order, _ = json_get("order", int)
    sku_id, _ = json_get("sku_id", int)
    article_id, _ = json_get("article_id", int)

    with conn.begin() as s:
        # Get category_item
        # Raise if category_item exists
        category_item = (
            s.query(CategoryItem)
            .filter_by(article_id=article_id, category_id=category_id, sku_id=sku_id)
            .first()
        )
        if category_item:
            return response(409, ApiText.HTTP_409)

        # Insert category_item
        category_item = CategoryItem(
            article_id=article_id, category_id=category_id, sku_id=sku_id, order=order
        )
        s.add(category_item)

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/categories/<int:category_id>/items/<int:item_id>")
def patch_categories_id_items_id(category_id: int, item_id: int) -> Response:
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get category_item
        # Raise if category_item doesn't exist
        category_item = (
            s.query(CategoryItem).filter_by(id=item_id, category_id=category_id).first()
        )
        if not category_item:
            return response(404, ApiText.HTTP_404)

        # Update CategoryItem
        if has_order:
            category_item.order_ = order

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/categories/<int:category_id>/items/<int:item_id>")
def delete_categories_id_items_id(category_id: int, item_id: int) -> Response:
    with conn.begin() as s:
        # Get category_item
        # Raise if category_item doesn't exist
        category_item = (
            s.query(CategoryItem).filter_by(id=item_id, category_id=category_id).first()
        )
        if not category_item:
            return response(404, ApiText.HTTP_404)

        # Delete category_item
        s.delete(category_item)

    return response()
