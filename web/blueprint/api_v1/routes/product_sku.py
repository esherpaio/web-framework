import itertools

from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import Product, ProductValue, Sku, SkuDetail, UserRoleLevel
from web.helper.api import ApiText, response
from web.helper.logger import logger
from web.helper.user import access_control
from web.helper.validation import gen_slug
from web.seeder.decorators import sync_after
from web.seeder.model.sku import SkuSyncer

#
# Configuration
#


#
# Endpoints
#



@api_v1_bp.post("/products/<int:product_id>/skus")
@access_control(UserRoleLevel.ADMIN)
@sync_after(SkuSyncer)
def post_skus(product_id: int) -> Response:
    with conn.begin() as s:
        # Get product and skus
        skus = s.query(Sku).filter_by(product_id=product_id).all()
        product = s.query(Product).filter_by(id=product_id).first()
        if product is None:
            return response(404, ApiText.HTTP_404)

        # Generate all possible combinations between value_ids
        value_id_sets = []
        options = [x for x in product.options if not x.is_deleted]
        for option in options:
            option_value_ids = [x.id for x in option.values if not x.is_deleted]
            value_id_sets.append(option_value_ids)
        value_id_groups = list(itertools.product(*value_id_sets))

        for value_ids in value_id_groups:
            for sku in skus:
                # Skip if sku already exists
                if sku.value_ids == sorted(value_ids):
                    logger.info("Restoring SKU %d", sku.id)
                    sku.is_deleted = False
                    break
            else:
                # Generate slug
                values = (
                    s.query(ProductValue)
                    .filter(ProductValue.id.in_(value_ids))
                    .order_by(ProductValue.id)
                    .all()
                )
                slug_parts = [product.name]
                for value in values:
                    slug_parts.append(value.name)
                slug = gen_slug("-".join(slug_parts))

                # Insert objects
                sku = Sku(
                    product_id=product_id, slug=slug, is_visible=True, unit_price=0
                )
                s.add(sku)
                s.flush()
                sku_details = [
                    SkuDetail(sku_id=sku.id, option_id=x.option_id, value_id=x.id)
                    for x in values
                ]
                s.add_all(sku_details)

    return response()


#
# Functions
#
