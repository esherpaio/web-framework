from sqlalchemy import JSON, CheckConstraint, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict, default_price


class Refund(Base):
    __tablename__ = "refund"
    __table_args__ = (CheckConstraint("total_price < 0"),)

    attributes = Column(JSON)
    mollie_id = Column(String(64), unique=True)
    number = Column(String(16), nullable=False, unique=True)
    total_price = Column(default_price, nullable=False)

    order_id = Column(FKRestrict("order.id"), nullable=False)

    order = relationship("Order", back_populates="refunds")

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
