from flask import Response
from sqlalchemy.orm import contains_eager

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import ProductOption, Sku, SkuDetail, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control
from web.helper.validation import gen_slug


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/options")
def post_products_id_options(product_id: int) -> Response:
    name, _ = json_get("name", str, nullable=False)
    order, _ = json_get("order", int)

    with conn.begin() as s:
        # Get option
        # Restore if option is deleted
        # Raise if option is not deleted
        product_option = (
            s.query(ProductOption)
            .filter_by(product_id=product_id, slug=gen_slug(name))
            .first()
        )
        if product_option:
            if product_option.is_deleted:
                product_option.is_deleted = False
            else:
                return response(409, ApiText.HTTP_409)

        else:
            # Insert option
            product_option = ProductOption(
                product_id=product_id, name=name, order=order
            )
            s.add(product_option)

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/products/<int:product_id>/options/<int:option_id>")
def patch_products_id_options_id(product_id: int, option_id: int) -> Response:
    order, has_order = json_get("order", int)

    with conn.begin() as s:
        # Get value
        # Raise if value doesn't exist
        product_option = (
            s.query(ProductOption)
            .filter_by(id=option_id, product_id=product_id)
            .first()
        )
        if not product_option:
            return response(404, ApiText.HTTP_404)

        # Update order
        if has_order:
            product_option.order = order

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/options/<int:option_id>")
def delete_products_id_options_id(product_id: int, option_id: int) -> Response:
    with conn.begin() as s:
        # Get option
        # Raise if option doesn't exist
        product_option = (
            s.query(ProductOption)
            .filter_by(id=option_id, product_id=product_id)
            .first()
        )
        if not product_option:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        product_option.is_deleted = True

        # Update skus
        skus = (
            s.query(Sku)
            .join(Sku.details)
            .options(contains_eager(Sku.details))
            .filter(SkuDetail.option_id == option_id)
            .all()
        )
        for sku in skus:
            sku.is_deleted = True

    return response()
