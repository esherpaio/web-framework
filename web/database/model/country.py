from typing import Any

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKRestrict
from ._validation import get_upper, val_length


class Country(Base):
    __tablename__ = "country"

    code = Column(String(2), nullable=False, unique=True)
    in_sitemap = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False, unique=True)

    currency_id = Column(FKRestrict("currency.id"), nullable=False)
    region_id = Column(FKRestrict("region.id"), nullable=False)

    currency = relationship("Currency")
    region = relationship("Region")

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(value, min_=2, max_=2)
        value = get_upper(value)
        return value
