from werkzeug import Response

from web.api.utils import ApiText, json_get, json_response
from web.auth import secure
from web.blueprint.api_v1 import api_v1_bp
from web.database import conn
from web.database.model import ProductLink, UserRoleLevel

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/products/<int:product_id>/links")
@secure(UserRoleLevel.ADMIN)
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
            return json_response(409, ApiText.HTTP_409)

        # Insert product link
        product_link = ProductLink(
            product_id=product_id, type_id=type_id, sku_id=sku_id
        )
        s.add(product_link)

    return json_response()


@api_v1_bp.delete("/products/<int:product_id>/links/<int:link_id>")
@secure(UserRoleLevel.ADMIN)
def delete_products_id_links_id(product_id: int, link_id: int) -> Response:
    with conn.begin() as s:
        # Delete product link
        product_link = (
            s.query(ProductLink).filter_by(id=link_id, product_id=product_id).first()
        )
        if not product_link:
            return json_response(404, ApiText.HTTP_404)
        s.delete(product_link)

    return json_response()


#
# Functions
#
