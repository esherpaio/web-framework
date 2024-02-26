from typing import Any

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Base
from ._utils import default_price, val_number


class OrderLine(Base):
    __tablename__ = "order_line"
    __table_args__ = (UniqueConstraint("order_id", "sku_id"),)

    quantity = MC(Integer, nullable=False)
    total_price = MC(default_price, nullable=False)

    order_id = MC(ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    sku_id = MC(ForeignKey("sku.id", ondelete="RESTRICT"), nullable=False)

    order = relationship("Order", back_populates="lines", lazy="joined")
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
