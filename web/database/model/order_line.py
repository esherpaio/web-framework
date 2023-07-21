from typing import Any

from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKCascade, FKRestrict, default_price
from ._validation import val_number


class OrderLine(Base):
    __tablename__ = "order_line"
    __table_args__ = (UniqueConstraint("order_id", "sku_id"),)

    quantity = Column(Integer, nullable=False)
    total_price = Column(default_price, nullable=False)

    order_id = Column(FKCascade("order.id"), nullable=False)
    sku_id = Column(FKRestrict("sku.id"), nullable=False)

    order = relationship("Order", back_populates="lines")
    sku = relationship("Sku")

    # Validations

    @validates("quantity")
    def validate_quantity(self, key: str, value: Any) -> Any:
        val_number(value, min_=1)
        return value

    @validates("total_price")
    def validate_total_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value

    # Properties - pricing

    @hybrid_property
    def total_price_vat(self) -> float:
        return self.total_price * self.order.vat_rate
