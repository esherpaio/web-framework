from flask import Response

from webshop.blueprint.api_v1 import api_v1_bp
from webshop.database.client import conn
from webshop.database.model import ProductLink, UserRoleLevel
from webshop.helper.api import response, ApiText, json_get
from webshop.helper.security import authorize


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/links")
def post_products_id_links(product_id: int) -> Response:
    sku_id, _ = json_get("sku_id", int, nullable=False)
    type_id, _ = json_get("type_id", int, nullable=False)

    with conn.begin() as s:
        # Get product_link
        # Raise if product_link exists
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

        # Insert product_link
        product_link = ProductLink(
            product_id=product_id, type_id=type_id, sku_id=sku_id
        )
        s.add(product_link)

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/links/<int:link_id>")
def delete_products_id_links_id(product_id: int, link_id: int) -> Response:
    with conn.begin() as s:
        # Get product_link
        # Raise if product_link doesn't exist
        product_link = (
            s.query(ProductLink).filter_by(id=link_id, product_id=product_id).first()
        )
        if not product_link:
            return response(404, ApiText.HTTP_404)

        # Update product_link
        s.delete(product_link)

    return response()
