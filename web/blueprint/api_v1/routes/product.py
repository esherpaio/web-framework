from werkzeug import Response

from web.blueprint.api_v1 import api_v1_bp
from web.database.client import conn
from web.database.model import CategoryItem, Product, ProductTypeId, Sku, UserRoleLevel
from web.libs.api import ApiText, json_get, response
from web.libs.auth import access_control
from web.libs.parse import gen_slug
from web.seeder.seed.sku import SkuSyncer
from web.seeder.utils import sync_after

#
# Configuration
#


#
# Endpoints
#


@api_v1_bp.post("/products")
@access_control(UserRoleLevel.ADMIN)
@sync_after(SkuSyncer)
def post_products() -> Response:
    name, _ = json_get("name", str, nullable=False)

    with conn.begin() as s:
        # Get or restore product
        product = s.query(Product).filter_by(slug=gen_slug(name)).first()
        if product:
            if product.is_deleted:
                product.is_deleted = False
                return response()
            else:
                return response(409, ApiText.HTTP_409)

        # Insert product
        product = Product(type_id=ProductTypeId.PHYSICAL, name=name, unit_price=1)
        s.add(product)

    return response()


@api_v1_bp.patch("/products/<int:product_id>")
@access_control(UserRoleLevel.ADMIN)
@sync_after(SkuSyncer)
def patch_products_id(product_id: int) -> Response:
    attributes, has_attributes = json_get("attributes", dict, default={})
    file_url, has_file_url = json_get("file_url", str)
    consent_required, has_consent_required = json_get("consent_required", bool)
    shipment_class_id, has_shipment_class_id = json_get("shipment_class_id", int)
    summary, has_summary = json_get("summary", str)
    type_id, has_type_id = json_get("type_id", int)
    unit_price, has_unit_price = json_get("unit_price", int | float)

    with conn.begin() as s:
        # Get product
        product = s.query(Product).filter_by(id=product_id).first()
        if product is None:
            return response(404, ApiText.HTTP_404)

        # Update product
        if has_attributes:
            product.attributes = attributes
        if has_type_id:
            product.type_id = type_id
        if has_shipment_class_id:
            product.shipment_class_id = shipment_class_id
        if has_summary:
            product.summary = summary
        if has_unit_price:
            product.unit_price = unit_price
        if has_consent_required:
            product.consent_required = consent_required
        if has_file_url:
            product.file_url = file_url

    return response()


@api_v1_bp.delete("/products/<int:product_id>")
@access_control(UserRoleLevel.ADMIN)
def delete_products_id(product_id: int) -> Response:
    with conn.begin() as s:
        # Delete product
        product = s.query(Product).filter_by(id=product_id).first()
        if not product:
            return response(404, ApiText.HTTP_404)
        product.is_deleted = True

        # Delete skus
        skus = s.query(Sku).filter(Sku.product_id == product_id).all()
        for sku in skus:
            sku.is_deleted = True

            # Delete category items
            category_items = s.query(CategoryItem).filter_by(sku_id=sku.id).all()
            for category_item in category_items:
                s.delete(category_item)

    return response()


#
# Functions
#
