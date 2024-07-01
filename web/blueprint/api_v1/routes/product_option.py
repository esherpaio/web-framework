from sqlalchemy import false
from sqlalchemy.orm import contains_eager
from werkzeug import Response

from web.api.utils import ApiText, json_get, json_response
from web.blueprint.api_v1 import api_v1_bp
from web.database import conn
from web.database.model import (
    ProductOption,
    ProductValue,
    Sku,
    SkuDetail,
    UserRoleLevel,
)
from web.libs.parse import gen_slug
from web.security import secure

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/products/<int:product_id>/options")
@secure(UserRoleLevel.ADMIN)
def post_products_id_options(product_id: int) -> Response:
    name, _ = json_get("name", str, nullable=False)
    order, _ = json_get("order", int)

    with conn.begin() as s:
        # Get or restore product option
        product_option = (
            s.query(ProductOption)
            .filter_by(product_id=product_id, slug=gen_slug(name))
            .first()
        )
        if product_option:
            if product_option.is_deleted:
                product_option.is_deleted = False
                return json_response()
            else:
                return json_response(409, ApiText.HTTP_409)

        # Insert product option
        product_option = ProductOption(product_id=product_id, name=name, order=order)
        s.add(product_option)

    return json_response()


@api_v1_bp.patch("/products/<int:product_id>/options/<int:option_id>")
@secure(UserRoleLevel.ADMIN)
def patch_products_id_options_id(product_id: int, option_id: int) -> Response:
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get product option
        product_option = (
            s.query(ProductOption)
            .filter_by(id=option_id, product_id=product_id)
            .first()
        )
        if not product_option:
            return json_response(404, ApiText.HTTP_404)

        # Update product option
        if has_order:
            product_option.order = order

    return json_response()


@api_v1_bp.delete("/products/<int:product_id>/options/<int:option_id>")
@secure(UserRoleLevel.ADMIN)
def delete_products_id_options_id(product_id: int, option_id: int) -> Response:
    with conn.begin() as s:
        # Delete product option
        product_option = (
            s.query(ProductOption)
            .filter_by(id=option_id, product_id=product_id)
            .first()
        )
        if not product_option:
            return json_response(404, ApiText.HTTP_404)
        product_option.is_deleted = True
        s.flush()

        # Delete product values
        product_values = (
            s.query(ProductValue).filter_by(option_id=option_id, is_deleted=False).all()
        )
        for product_value in product_values:
            product_value.is_deleted = True
        s.flush()

        # Delete skus
        skus = (
            s.query(Sku)
            .join(Sku.details)
            .options(contains_eager(Sku.details))
            .filter(SkuDetail.option_id == option_id, Sku.is_deleted == false())
            .all()
        )
        for sku in skus:
            sku.is_deleted = True

    return json_response()


#
# Functions
#
