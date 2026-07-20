from typing import TYPE_CHECKING

from sqlalchemy import true
from sqlalchemy.orm import Session, joinedload

from web.database.model import Country, ShipmentMethod

if TYPE_CHECKING:
    from web.app.schema import ShippingItem


def get_shipment_method_countries(
    s: Session,
    method: ShipmentMethod,
) -> list[Country]:
    zone = method.zone
    if zone is None:
        return []
    if zone.country_id is not None:
        return [zone.country] if zone.country else []
    if zone.region_id is not None:
        return (
            s.query(Country)
            .options(joinedload(Country.currency))
            .filter(
                Country.region_id == zone.region_id,
                Country.allows_shipping == true(),
            )
            .all()
        )
    return []


def gen_shipping_items(
    s: Session,
    methods: list[ShipmentMethod],
) -> list["ShippingItem"]:
    per_country: dict[str, set[tuple]] = {}
    for method in methods:
        for country in get_shipment_method_countries(s, method):
            currency = country.currency
            rate = round(float(method.unit_price * currency.rate), 2)
            option = (rate, method.min_days, method.max_days, currency.code)
            per_country.setdefault(country.code, set()).add(option)

    groups: dict[tuple, list[str]] = {}
    for code, options in per_country.items():
        for option in options:
            groups.setdefault(option, []).append(code)

    items: list[ShippingItem] = []
    for (rate, min_days, max_days, currency_code), countries in groups.items():
        item: ShippingItem = {
            "countries": countries,
            "rate": rate,
            "currency": currency_code,
        }
        if min_days is not None:
            item["min_days"] = min_days
        if max_days is not None:
            item["max_days"] = max_days
        items.append(item)
    return items
