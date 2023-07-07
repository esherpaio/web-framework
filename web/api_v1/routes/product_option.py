from flask import Response
from sqlalchemy.orm import contains_eager

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import (
    ProductOption,
    ProductValue,
    Sku,
    SkuDetail,
    UserRoleLevel,
)
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control
from web.helper.validation import gen_slug


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/options")
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
                return response()
            else:
                return response(409, ApiText.HTTP_409)

        # Insert product option
        product_option = ProductOption(product_id=product_id, name=name, order=order)
        s.add(product_option)

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/products/<int:product_id>/options/<int:option_id>")
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
            return response(404, ApiText.HTTP_404)

        # Update product option
        if has_order:
            product_option.order = order

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/options/<int:option_id>")
def delete_products_id_options_id(product_id: int, option_id: int) -> Response:
    with conn.begin() as s:
        # Delete product option
        product_option = (
            s.query(ProductOption)
            .filter_by(id=option_id, product_id=product_id)
            .first()
        )
        if not product_option:
            return response(404, ApiText.HTTP_404)
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
            .filter(SkuDetail.option_id == option_id, Sku.is_deleted is False)
            .all()
        )
        for sku in skus:
            sku.is_deleted = True

    return response()
