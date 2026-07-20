from typing import TYPE_CHECKING

from sqlalchemy import true
from sqlalchemy.orm import Session

from web.database.model import Country, ShipmentMethod
from web.locale import current_locale

if TYPE_CHECKING:
    from web.app.schema import ShippingItem


def gen_shipping_items(
    s: Session,
    methods: list[ShipmentMethod],
) -> list["ShippingItem"]:
    currency = current_locale.currency
    groups: dict[tuple, list[str]] = {}
    for method in methods:
        zone = method.zone
        if zone is None:
            continue
        if zone.country_id is not None:
            country_codes = [zone.country.code] if zone.country else []
        elif zone.region_id is not None:
            country_codes = [
                code
                for (code,) in s.query(Country.code)
                .filter(
                    Country.region_id == zone.region_id,
                    Country.allows_shipping == true(),
                )
                .all()
            ]
        else:
            country_codes = []
        if not country_codes:
            continue

        # Grouping by country
        key = (
            round(float(method.unit_price * currency.rate), 2),
            currency.code,
            method.min_days,
            method.max_days,
        )
        bucket = groups.setdefault(key, [])
        for code in country_codes:
            if code not in bucket:
                bucket.append(code)

    items: list[ShippingItem] = []
    for (rate, currency_code, min_days, max_days), countries in groups.items():
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
