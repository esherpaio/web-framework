from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Attribute, Base
from ._utils import default_price, val_number


class Sku(Base, Attribute):
    __tablename__ = "sku"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    is_visible = MC(Boolean, nullable=False, default=False, server_default="false")
    number = MC(String(64), unique=True)
    slug = MC(String(128), unique=True, nullable=False)
    stock = MC(Integer, nullable=False, default=0, server_default="0")
    unit_price = MC(default_price, nullable=False)

    product_id = MC(ForeignKey("product.id", ondelete="RESTRICT"), nullable=False)
    route_id = MC(ForeignKey("app_route.id", ondelete="SET NULL"))

    details = relationship("SkuDetail", back_populates="sku")
    product = relationship("Product", viewonly=True)
    route = relationship("AppRoute")

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
