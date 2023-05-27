from flask import Response
from sqlalchemy.orm import contains_eager

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import ProductValue, Sku, SkuDetail, UserRoleLevel
from web.helper.api import ApiText, json_get, response
from web.helper.security import authorize
from web.helper.validation import gen_slug
from web.seeder.decs import sync_after
from web.seeder.model.sku import SkuSyncer


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products/<int:product_id>/values")
def post_products_id_values(product_id: int) -> Response:
    name, _ = json_get("name", str, nullable=False)
    option_id, _ = json_get("option_id", int, nullable=False)
    order, _ = json_get("order", int)
    unit_price, _ = json_get("unit_price", int | float, nullable=True)

    with conn.begin() as s:
        # Get value
        # Restore if value is deleted
        # Raise if value is not deleted
        product_value = (
            s.query(ProductValue)
            .filter_by(option_id=option_id, slug=gen_slug(name))
            .first()
        )
        if product_value:
            if product_value.is_deleted:
                product_value.is_deleted = False
            else:
                return response(409, ApiText.HTTP_409)

        else:
            # Insert value
            product_value = ProductValue(
                option_id=option_id, name=name, unit_price=unit_price, order=order
            )
            s.add(product_value)

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/products/<int:product_id>/values/<int:value_id>")
@sync_after(SkuSyncer)
def patch_products_id_values_id(product_id: int, value_id: int) -> Response:
    media_id, has_media_id = json_get("media_id", int)
    order, has_order = json_get("order", int)
    unit_price, has_unit_price = json_get("unit_price", int | float)

    with conn.begin() as s:
        # Get value
        # Raise if value doesn't exist
        product_value = s.query(ProductValue).filter_by(id=value_id).first()
        if not product_value:
            return response(404, ApiText.HTTP_404)

        # Update media_id
        if has_media_id:
            product_value.media_id = media_id

        # Update unit_price
        if has_unit_price:
            product_value.unit_price = unit_price

        # Updat order
        if has_order:
            product_value.order_ = order

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>/values/<int:value_id>")
def delete_products_id_values_id(product_id: int, value_id: int) -> Response:
    with conn.begin() as s:
        # Get value
        # Raise if value doesn't exist
        product_value = s.query(ProductValue).filter_by(id=value_id).first()
        if not product_value:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        product_value.is_deleted = True

        # Update skus
        skus = (
            s.query(Sku)
            .join(Sku.details)
            .options(contains_eager(Sku.details))
            .filter(SkuDetail.value_id == value_id)
            .all()
        )
        for sku in skus:
            sku.is_deleted = True

    return response()
