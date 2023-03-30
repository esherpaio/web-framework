from sqlalchemy import Column, String, Boolean, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ..utils import FKCascade, price


class Sku(Base):
    __tablename__ = "sku"
    __table_args__ = (CheckConstraint("unit_price >= 0"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=False)
    slug = Column(String(128), unique=True, nullable=False)
    unit_price = Column(price, nullable=False)

    product_id = Column(FKCascade("product.id"), nullable=False)

    details = relationship("SkuDetail", back_populates="sku")
    product = relationship("Product")

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
