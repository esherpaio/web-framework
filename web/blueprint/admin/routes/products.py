from flask import redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload
from werkzeug import Response

from web.blueprint.admin import admin_bp
from web.database.client import conn
from web.database.model import (
    Category,
    Product,
    ProductLink,
    ProductMedia,
    ProductOption,
    ProductValue,
    ShipmentClass,
    Sku,
    SkuDetail,
)


@admin_bp.get("/admin/products")
def products() -> str:
    with conn.begin() as s:
        products_ = (
            s.query(Product)
            .options(joinedload(Product.shipment_class))
            .filter_by(is_deleted=False)
            .order_by(Product.name)
            .all()
        )

    return render_template(
        "admin/products.html",
        products=products_,
    )


@admin_bp.get("/admin/products/<int:product_id>")
def product(product_id: int) -> str | Response:
    tab = request.args.get("tab", "general", type=str)

    with conn.begin() as s:
        product_ = (
            s.query(Product)
            .options(
                joinedload(Product.type),
                joinedload(Product.shipment_class),
            )
            .filter_by(id=product_id, is_deleted=False)
            .first()
        )
        if not product_:
            return redirect(url_for("admin.error"))

        categories = s.query(Category).order_by(Category.name).all()
        shipment_classes = (
            s.query(ShipmentClass)
            .filter_by(is_deleted=False)
            .order_by(ShipmentClass.name, ShipmentClass.id)
            .all()
        )
        product_options = (
            s.query(ProductOption)
            .options(joinedload(ProductOption.values))
            .filter_by(product_id=product_id, is_deleted=False)
            .order_by(ProductOption.order, ProductOption.id)
            .all()
        )
        product_medias = (
            s.query(ProductMedia)
            .options(joinedload(ProductMedia.file))
            .filter_by(product_id=product_id)
            .order_by(ProductMedia.order, ProductMedia.id)
            .all()
        )
        product_links = (
            s.query(ProductLink)
            .options(
                joinedload(ProductLink.type),
                joinedload(ProductLink.sku),
                joinedload(ProductLink.sku, Sku.product),
                joinedload(ProductLink.sku, Sku.details),
                joinedload(ProductLink.sku, Sku.details, SkuDetail.option),
                joinedload(ProductLink.sku, Sku.details, SkuDetail.value),
            )
            .filter_by(product_id=product_.id)
            .order_by(ProductLink.sku_id, ProductLink.type_id)
            .all()
        )
        available_skus = (
            s.query(Sku)
            .options(
                joinedload(Sku.product),
                joinedload(Sku.details),
                joinedload(Sku.details, SkuDetail.option),
                joinedload(Sku.details, SkuDetail.value),
            )
            .filter_by(is_deleted=False)
            .order_by(Sku.slug)
            .all()
        )
        skus = (
            s.query(Sku)
            .options(
                joinedload(Sku.details),
                joinedload(Sku.details, SkuDetail.option),
                joinedload(Sku.details, SkuDetail.value),
            )
            .filter_by(product_id=product_.id, is_deleted=False)
            .order_by(Sku.id)
            .all()
        )

    return render_template(
        "admin/product.html",
        tab=tab,
        product=product_,
        categories=categories,
        shipment_classes=shipment_classes,
        product_options=product_options,
        product_medias=product_medias,
        available_skus=available_skus,
        product_links=product_links,
        skus=skus,
    )


@admin_bp.get("/admin/products/<int:product_id>/options/<int:option_id>")
def product_option(product_id: int, option_id: int) -> str:
    with conn.begin() as s:
        product_ = s.query(Product).filter_by(id=product_id, is_deleted=False).first()
        option = (
            s.query(ProductOption)
            .filter_by(id=option_id, product_id=product_id, is_deleted=False)
            .first()
        )
        product_medias = (
            s.query(ProductMedia)
            .options(joinedload(ProductMedia.file))
            .filter_by(product_id=product_id)
            .order_by(ProductMedia.order, ProductMedia.id)
            .all()
        )
        option_values = (
            s.query(ProductValue)
            .options(joinedload(ProductValue.media))
            .filter_by(option_id=option_id, is_deleted=False)
            .order_by(ProductValue.order, ProductValue.id)
            .all()
        )

    return render_template(
        "admin/product_option.html",
        product=product_,
        option=option,
        product_medias=product_medias,
        option_values=option_values,
    )
