from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import ColumnElement

from web.database.model import Product, ProductValue, Sku, SkuDetail
from web.logger import log


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
