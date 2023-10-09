from typing import Any

from sqlalchemy import JSON, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKRestrict, default_price
from ._validation import val_number


class Refund(Base):
    __tablename__ = "refund"

    attributes = Column(
        MutableDict.as_mutable(JSON), nullable=False, server_default="{}"
    )
    mollie_id = Column(String(64), unique=True)
    number = Column(String(16), nullable=False, unique=True)
    total_price = Column(default_price, nullable=False)

    order_id = Column(FKRestrict("order.id"), nullable=False)

    order = relationship("Order", back_populates="refunds")

    # Validation

    @validates("total_price")
    def validate_total_price(self, key: str, value: Any) -> Any:
        val_number(value, max_=0)
        return value

    # Properties - pricing

    @hybrid_property
    def vat_rate(self) -> float:
        return self.order.vat_rate

    @hybrid_property
    def vat_percentage(self) -> int:
        return round((self.vat_rate - 1) * 100)

    @hybrid_property
    def vat_amount(self) -> float:
        return self.total_price_vat - self.total_price

    @hybrid_property
    def subtotal_price(self) -> float:
        return self.total_price

    @hybrid_property
    def subtotal_price_vat(self) -> float:
        return self.total_price * self.vat_rate

    @hybrid_property
    def total_price_vat(self) -> float:
        return self.total_price * self.vat_rate
