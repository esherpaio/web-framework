from flask import Response

from web.blueprint.api_v1 import api_v1_bp
from web.blueprint.api_v1.utils.product import clean_html
from web.database.client import conn
from web.database.model import Product, ProductTypeId, Sku, UserRoleLevel
from web.helper.api import ApiText, authorize, json_get, response
from web.helper.validation import gen_slug
from web.seeder.decorators import sync_after
from web.seeder.model.sku import SkuSyncer


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.post("/products")
@sync_after(SkuSyncer)
def post_products() -> Response:
    name, _ = json_get("name", str, nullable=False)

    with conn.begin() as s:
        # Get product
        # Restore if product is deleted
        # Raise if product is not deleted
        product = s.query(Product).filter_by(slug=gen_slug(name)).first()
        if product:
            if product.is_deleted:
                product.is_deleted = False
            else:
                return response(409, ApiText.HTTP_409)

        else:
            # Insert product
            product = Product(type_id=ProductTypeId.PHYSICAL, name=name, unit_price=1)
            s.add(product)
            s.flush()

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.patch("/products/<int:product_id>")
@sync_after(SkuSyncer)
def patch_products_id(product_id: int) -> Response:
    file_url, has_file_url = json_get("file_url", str)
    html, has_html = json_get("html", str)
    name, has_name = json_get("name", str)
    read_html, has_read_html = json_get("read_html", bool)
    shipment_class_id, has_shipment_class_id = json_get("shipment_class_id", int)
    summary, has_summary = json_get("summary", str)
    type_id, has_type_id = json_get("type_id", int)
    unit_price, has_unit_price = json_get("unit_price", int | float)

    with conn.begin() as s:
        # Get product
        # Raise if product doesn't exist
        product = s.query(Product).filter_by(id=product_id).first()
        if product is None:
            return response(404, ApiText.HTTP_404)

        # Update product
        if has_type_id:
            product.type_id = type_id
        if has_shipment_class_id:
            product.shipment_class_id = shipment_class_id
        if has_name:
            product.name = name
        if has_summary:
            product.summary = summary
        if has_html:
            product.html = clean_html(html)
        if has_unit_price:
            product.unit_price = unit_price
        if has_read_html:
            product.read_html = read_html
        if has_file_url:
            product.file_url = file_url
        s.flush()

    return response()


@authorize(UserRoleLevel.ADMIN)
@api_v1_bp.delete("/products/<int:product_id>")
def delete_products_id(product_id: int) -> Response:
    with conn.begin() as s:
        # Get product
        # Raise if product doesn't exist
        product = s.query(Product).filter_by(id=product_id).first()
        if not product:
            return response(404, ApiText.HTTP_404)

        # Update is_deleted
        product.is_deleted = True

        # Update SKUs
        skus = s.query(Sku).filter(Sku.product_id == product_id).all()
        for sku in skus:
            sku.is_deleted = True

    return response()
