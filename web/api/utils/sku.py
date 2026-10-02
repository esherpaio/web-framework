from decimal import Decimal

from flask import abort
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import ColumnElement

from web.api import HttpText, json_response
from web.database.model import Product, ProductValue, Sku, SkuDetail
from web.i18n import _
from web.logger import log


def val_sku(sku: Sku | None) -> None:
    if sku is None:
        abort(json_response(404, HttpText.HTTP_404))
    if sku.is_deleted or sku.product.is_deleted:
        abort(json_response(400, _("API_SKU_UNAVAILABLE")))


def get_sku_unit_price(product: Product, values: list[ProductValue]) -> Decimal:
    return product.unit_price + sum((x.unit_price for x in values), Decimal())


def set_sku_unit_prices(
    s: Session,
    sku_ids: list[int] | None = None,
    product_ids: list[int] | None = None,
    value_ids: list[int] | None = None,
) -> None:
    filters: list[ColumnElement[bool]] = []
    if sku_ids is not None:
        filters.append(Sku.id.in_(sku_ids))
    if product_ids is not None:
        filters.append(Sku.product_id.in_(product_ids))
    if value_ids is not None:
        filters.append(Sku.details.any(SkuDetail.value_id.in_(value_ids)))

    if not filters:
        log.warning("No filters to update SKUs")
        return

    skus = (
        s.query(Sku)
        .options(
            joinedload(Sku.product),
            joinedload(Sku.details).joinedload(SkuDetail.value),
        )
        .filter(*filters)
        .all()
    )
    for sku in skus:
        product = sku.product
        values = [x.value for x in sku.details]
        sku.unit_price = get_sku_unit_price(product, values)
