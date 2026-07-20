from typing import TYPE_CHECKING

from sqlalchemy import true
from sqlalchemy.orm import Session

from web.database.model import Country, ShipmentMethod
from web.locale import current_locale

if TYPE_CHECKING:
    from web.app.schema import ShippingItem


def _speed(option: tuple) -> tuple:
    _, min_days, max_days = option
    inf = float("inf")
    return (
        max_days if max_days is not None else inf,
        min_days if min_days is not None else inf,
    )


def _dominates(a: tuple, b: tuple) -> bool:
    if a == b:
        return False
    cheaper_or_equal = a[0] <= b[0]
    faster_or_equal = _speed(a) <= _speed(b)
    strictly_better = a[0] < b[0] or _speed(a) < _speed(b)
    return cheaper_or_equal and faster_or_equal and strictly_better


def _country_codes(s: Session, method: ShipmentMethod) -> list[str]:
    zone = method.zone
    if zone is None:
        return []
    if zone.country_id is not None:
        return [zone.country.code] if zone.country else []
    if zone.region_id is not None:
        return [
            code
            for (code,) in s.query(Country.code)
            .filter(
                Country.region_id == zone.region_id,
                Country.allows_shipping == true(),
            )
            .all()
        ]
    return []


def gen_shipping_items(
    s: Session,
    methods: list[ShipmentMethod],
) -> list["ShippingItem"]:
    currency = current_locale.currency
    # Collect every distinct shipping option per destination.
    per_country: dict[str, set[tuple]] = {}
    for method in methods:
        rate = round(float(method.unit_price * currency.rate), 2)
        option = (rate, method.min_days, method.max_days)
        for code in _country_codes(s, method):
            per_country.setdefault(code, set()).add(option)

    # Keep only non-dominated options, grouped by identical option.
    groups: dict[tuple, list[str]] = {}
    for code, options in per_country.items():
        for option in options:
            if not any(_dominates(other, option) for other in options):
                groups.setdefault(option, []).append(code)

    items: list[ShippingItem] = []
    for (rate, min_days, max_days), countries in groups.items():
        item: ShippingItem = {
            "countries": countries,
            "rate": rate,
            "currency": currency.code,
        }
        if min_days is not None:
            item["min_days"] = min_days
        if max_days is not None:
            item["max_days"] = max_days
        items.append(item)
    return items
