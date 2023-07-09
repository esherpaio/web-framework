import itertools

from flask import Response

from web.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import (
    CategoryItem,
    Product,
    ProductValue,
    Sku,
    SkuDetail,
    UserRoleLevel,
)
from web.helper.api import ApiText, json_get, response
from web.helper.user import access_control
from web.helper.validation import gen_slug
from web.seeder.decorators import sync_after
from web.seeder.model.sku import SkuSyncer


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.post("/skus")
@sync_after(SkuSyncer)
def post_skus() -> Response:
    product_id, _ = json_get("product_id", int, nullable=False)

    with conn.begin() as s:
        # Get product and skus
        product = s.query(Product).filter_by(id=product_id).first()
        if not product:
            return response(404, ApiText.HTTP_404)
        skus = s.query(Sku).filter_by(product_id=product_id).all()

        # Generate all possible combinations between value_ids
        value_id_sets = []
        options = [x for x in product.options if not x.is_deleted]
        for option in options:
            value_ids = [x.id for x in option.values if not x.is_deleted]
            value_id_sets.append(value_ids)
        value_id_groups = list(itertools.product(*value_id_sets))

        for value_ids in value_id_groups:
            # Skip if sku already exists
            for sku in skus:
                if sorted(sku.value_ids) == sorted(value_ids):
                    sku.in_header = True
                    sku.is_deleted = False
                    break

            else:
                # Get product values
                values = (
                    s.query(ProductValue)
                    .filter(ProductValue.id.in_(value_ids))
                    .order_by(ProductValue.id)
                    .all()
                )

                # Generate slug
                slug_parts = [product.name]
                for value in values:
                    slug_parts.append(value.name)
                slug = gen_slug("-".join(slug_parts))

                # Insert sku
                sku = Sku(
                    product_id=product_id,
                    slug=slug,
                    is_visible=True,
                    unit_price=0,
                )
                s.add(sku)
                s.flush()

                # Insert sku_details
                for value in values:
                    sku_detail = SkuDetail(
                        sku_id=sku.id,
                        option_id=value.option_id,
                        value_id=value.id,
                    )
                    s.add(sku_detail)
                    s.flush()

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/skus/<int:sku_id>")
def patch_skus_id(sku_id: int) -> Response:
    attributes, has_attributes = json_get("attributes", dict, default={})
    is_visible, has_is_visible = json_get("is_visible", bool)

    with conn.begin() as s:
        # Get sku
        sku = s.query(Sku).filter_by(id=sku_id).first()
        if not sku:
            return response(404, ApiText.HTTP_404)

        # Update sku
        if has_attributes:
            sku.attributes = attributes
        if has_is_visible:
            sku.is_visible = is_visible

    return response()


@access_control(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/skus/<int:sku_id>")
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

    return response()
