from datetime import datetime, timezone
from decimal import Decimal

import pyvat
from pyvat import ItemType, Party, VatChargeAction

from web.setup import settings


def get_vat(country_code: str, is_business: bool) -> tuple[Decimal, bool]:
    """Get VAT information.

    Args:
        country_code: ISO 3166-1 alpha-2 country code.
        is_business: Whether it is a business.

    Returns:
        vat_rate: The VAT rate.
        vat_reverse: Whether the VAT is reverse charged.
    """
    date = datetime.now(timezone.utc).date()
    type_ = ItemType.generic_electronic_service
    buyer = Party(country_code, is_business)
    seller = Party(settings.BUSINESS_COUNTRY_CODE, True)
    vat = pyvat.get_sale_vat_charge(date, type_, buyer, seller)
    if vat.action == VatChargeAction.charge:
        vat_rate = (vat.rate / Decimal("100")) + Decimal("1")
        vat_reverse = False
    elif vat.action == VatChargeAction.reverse_charge:
        vat_rate = Decimal("1")
        vat_reverse = False
    elif vat.action == VatChargeAction.no_charge:
        vat_rate = Decimal("1")
        vat_reverse = True
    else:
        raise NotImplementedError(f"Unknown VAT action: {vat.action}")
    return vat_rate, vat_reverse
