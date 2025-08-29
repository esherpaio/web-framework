from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import IntBase
from ._utils import get_upper, val_length


class Country(IntBase):
    __tablename__ = "country"

    code = MC(String(2), nullable=False, unique=True)
    in_sitemap = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False, unique=True)
    requires_billing_state = MC(
        Boolean, nullable=False, default=False, server_default="false"
    )
    requires_billing_vat = MC(
        Boolean, nullable=False, default=False, server_default="false"
    )
    allows_shipping = MC(Boolean, nullable=False, default=True, server_default="true")

    currency_id = MC(ForeignKey("currency.id", ondelete="RESTRICT"), nullable=False)
    region_id = MC(ForeignKey("region.id", ondelete="RESTRICT"), nullable=False)

    currency = relationship("Currency")
    region = relationship("Region")

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(key, value, min_=2, max_=2)
        value = get_upper(value)
        return value
