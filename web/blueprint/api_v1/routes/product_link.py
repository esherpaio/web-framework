from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import ProductLink, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control

#
# Configuration
#


#
# Endpoints
#


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/links")
def post_products_id_links(product_id: int) -> Response:
    sku_id, _ = json_get("sku_id", int, nullable=False)
    type_id, _ = json_get("type_id", int, nullable=False)

    with conn.begin() as s:
        # Check if product link already exists
        product_link = (
            s.query(ProductLink)
            .filter_by(
                product_id=product_id,
                type_id=type_id,
                sku_id=sku_id,
            )
            .first()
        )
        if product_link:
            return response(409, ApiText.HTTP_409)

        # Insert product link
        product_link = ProductLink(
            product_id=product_id, type_id=type_id, sku_id=sku_id
        )
        s.add(product_link)

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/links/<int:link_id>")
def delete_products_id_links_id(product_id: int, link_id: int) -> Response:
    with conn.begin() as s:
        # Delete product link
        product_link = (
            s.query(ProductLink).filter_by(id=link_id, product_id=product_id).first()
        )
        if not product_link:
            return response(404, ApiText.HTTP_404)
        s.delete(product_link)

    return response()
