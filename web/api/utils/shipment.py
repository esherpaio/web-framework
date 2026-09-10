from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import false, or_
from sqlalchemy.orm import Session

from web.database.model import (
    Country,
    Currency,
    ShipmentClass,
    ShipmentMethod,
    ShipmentZone,
)

if TYPE_CHECKING:
    from web.app.schema import ShippingItem


def select_shipment_methods(
    s: Session,
    class_ids: list[int] | int | None,
    country: Country,
) -> list[ShipmentMethod]:
    if isinstance(class_ids, int):
        class_ids = [class_ids]
    if not class_ids:
        return []

    class_ = (
        s.query(ShipmentClass)
        .filter(
            ShipmentClass.id.in_(class_ids),
            ShipmentClass.is_deleted == false(),
        )
        .order_by(ShipmentClass.order)
        .first()
    )
    zone_ = (
        s.query(ShipmentZone)
        .filter(
            or_(
                ShipmentZone.country_id == country.id,
                ShipmentZone.region_id == country.region_id,
            ),
            ShipmentZone.is_deleted == false(),
        )
        .order_by(ShipmentZone.order)
        .first()
    )
    if class_ is None or zone_ is None:
        return []

    methods = (
        s.query(ShipmentMethod)
        .filter_by(
            class_id=class_.id,
            zone_id=zone_.id,
            is_deleted=False,
        )
        .order_by(ShipmentMethod.unit_price)
        .all()
    )
    return methods


def gen_shipping_items(
    methods: list[ShipmentMethod],
    country: Country,
    currency: Currency,
    vat_rate: Decimal,
) -> list["ShippingItem"]:
    items: list[ShippingItem] = []
    for method in methods:
        item: ShippingItem = {
            "countries": [country.code],
            "rate": method.get_price(currency=currency, vat_rate=vat_rate),
            "currency": currency.code,
        }
        if method.min_days is not None:
            item["min_days"] = method.min_days
        if method.max_days is not None:
            item["max_days"] = method.max_days
        items.append(item)
    return items
