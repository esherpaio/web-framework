from typing import Any

from sqlalchemy import JSON, Boolean, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKRestrict, default_price
from ._validation import val_number


class Sku(Base):
    __tablename__ = "sku"

    attributes = Column(JSON, nullable=False, server_default="{}")
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=False)
    slug = Column(String(128), unique=True, nullable=False)
    unit_price = Column(default_price, nullable=False)

    product_id = Column(FKRestrict("product.id"), nullable=False)

    category_items = relationship("CategoryItem", back_populates="sku")
    details = relationship("SkuDetail", back_populates="sku")
    product = relationship("Product")

    # Validation

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value

    # Properties - general

    @hybrid_property
    def name(self) -> str:
        parts = [self.product.name]
        for detail in self.details:
            parts.append(detail.value.name)
        return " ".join(parts)

    # Properties - details

    @hybrid_property
    def option_ids(self) -> list[int]:
        return sorted([x.option_id for x in self.details])

    @hybrid_property
    def value_ids(self) -> list[int]:
        return sorted([x.value_id for x in self.details])
