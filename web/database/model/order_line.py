from sqlalchemy import CheckConstraint, Column, Integer, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade, FKRestrict, price


class OrderLine(Base):
    __tablename__ = "order_line"
    __table_args__ = (
        CheckConstraint("quantity >= 1"),
        CheckConstraint("total_price >= 0"),
        UniqueConstraint("order_id", "sku_id"),
    )

    quantity = Column(Integer, nullable=False)
    total_price = Column(price, nullable=False)

    order_id = Column(FKCascade("order.id"), nullable=False)
    sku_id = Column(FKRestrict("sku.id"), nullable=False)

    order = relationship("Order", back_populates="lines")
    sku = relationship("Sku")

    # Properties - pricing

    @hybrid_property
    def total_price_vat(self) -> float:
        return self.total_price * self.order.vat_rate
