from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import default_price, type_json
from ._validation import val_number


class Sku(Base):
    __tablename__ = "sku"

    attributes = MC(type_json, nullable=False, server_default="{}")
    is_deleted = MC(Boolean, nullable=False, default=False)
    is_visible = MC(Boolean, nullable=False, default=False)
    slug = MC(String(128), unique=True, nullable=False)
    unit_price = MC(default_price, nullable=False)

    product_id = MC(ForeignKey("product.id", ondelete="RESTRICT"), nullable=False)

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
