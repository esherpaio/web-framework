from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKCascade, FKSetNull, default_price
from ._validation import get_slug, val_number


class ProductValue(Base):
    __tablename__ = "product_value"
    __table_args__ = (UniqueConstraint("option_id", "slug"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    order = Column(Integer)
    slug = Column(String(64), nullable=False)
    unit_price = Column(default_price, nullable=False, default=0)

    media_id = Column(FKSetNull("product_media.id"))
    option_id = Column(FKCascade("product_option.id"), nullable=False)

    media = relationship("ProductMedia")
    option = relationship("ProductOption", back_populates="values")

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value
