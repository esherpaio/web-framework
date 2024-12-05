from flask import render_template
from sqlalchemy.orm import joinedload

from web.app.blueprint.admin_v1 import admin_v1_bp
from web.auth import current_user
from web.database import conn
from web.database.model import (
    Cart,
    CartItem,
    Product,
    ProductMedia,
    Sku,
    SkuDetail,
)


@admin_v1_bp.get("/admin/cart")
def cart() -> str:
    with conn.begin() as s:
        # fmt: off
        cart_ = (
            s.query(Cart)
            .options(
                joinedload(Cart.currency),
                joinedload(Cart.coupon),
                joinedload(Cart.items),
                joinedload(Cart.items, CartItem.cart),
                joinedload(Cart.items, CartItem.sku),
                joinedload(Cart.items, CartItem.sku, Sku.product),
            )
            .filter_by(user_id=current_user.id)
            .first()
        )
        cart_items = (
            s.query(CartItem)
            .options(
                joinedload(CartItem.cart),
                joinedload(CartItem.cart, Cart.currency),
                joinedload(CartItem.sku),
                joinedload(CartItem.sku, Sku.product),
                joinedload(CartItem.sku, Sku.product, Product.medias),
                joinedload(CartItem.sku, Sku.product, Product.medias, ProductMedia.file),
                joinedload(CartItem.sku, Sku.details),
                joinedload(CartItem.sku, Sku.details, SkuDetail.option),
                joinedload(CartItem.sku, Sku.details, SkuDetail.value),
            )
            .filter_by(cart_id=cart_.id if cart_ else None)
            .order_by(CartItem.id.desc())
            .all()
        )
        # fmt: on

    return render_template(
        "admin/cart.html",
        cart=cart_,
        cart_items=cart_items,
    )
