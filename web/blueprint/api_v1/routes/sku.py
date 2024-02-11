from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import CategoryItem, ProductLink, Sku, UserRoleLevel
from web.libs.api import ApiText, json_get, response
from web.libs.auth import access_control

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.patch("/skus/<int:sku_id>")
@access_control(UserRoleLevel.ADMIN)
def patch_skus_id(sku_id: int) -> Response:
    attributes, has_attributes = json_get("attributes", dict, default={})
    stock, has_stock = json_get("stock", int)
    number, has_number = json_get("number", str)

    with conn.begin() as s:
        # Get sku
        sku = s.query(Sku).filter_by(id=sku_id).first()
        if not sku:
            return response(404, ApiText.HTTP_404)

        # Update sku
        if has_attributes:
            sku.attributes = attributes
        if has_stock:
            sku.stock = stock
        if has_number:
            sku.number = number

    return response()


@api_v1_bp.delete("/skus/<int:sku_id>")
@access_control(UserRoleLevel.ADMIN)
def delete_skus_id(sku_id: int) -> Response:
    with conn.begin() as s:
        # Delete sku
        sku = s.query(Sku).filter_by(id=sku_id).first()
        if not sku:
            return response(404, ApiText.HTTP_404)
        sku.is_deleted = True

        # Delete category items
        category_items = s.query(CategoryItem).filter_by(sku_id=sku_id).all()
        for category_item in category_items:
            s.delete(category_item)

        # Delete product links
        product_links = s.query(ProductLink).filter_by(sku_id=sku_id).all()
        for product_link in product_links:
            s.delete(product_link)

    return response()


#
# Functions
#
