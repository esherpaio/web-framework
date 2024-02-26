from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Base
from ._utils import get_upper, val_length


class Country(Base):
    __tablename__ = "country"

    code = MC(String(2), nullable=False, unique=True)
    in_sitemap = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False, unique=True)
    state_required = MC(Boolean, nullable=False, default=False)

    currency_id = MC(ForeignKey("currency.id", ondelete="RESTRICT"), nullable=False)
    region_id = MC(ForeignKey("region.id", ondelete="RESTRICT"), nullable=False)

    currency = relationship("Currency")
    region = relationship("Region")

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(value, min_=2, max_=2)
        value = get_upper(value)
        return value
