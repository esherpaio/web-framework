from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Attribute, Base


class Invoice(Base, Attribute):
    __tablename__ = "invoice"

    expires_at = MC(DateTime())
    number = MC(String(16), nullable=False, unique=True)
    paid_at = MC(DateTime())

    order_id = MC(
        ForeignKey("order.id", ondelete="RESTRICT"), nullable=False, unique=True
    )

    order = relationship("Order", back_populates="invoice")
