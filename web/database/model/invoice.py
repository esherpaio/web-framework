from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from . import Base
from ._utils import type_json


class Invoice(Base):
    __tablename__ = "invoice"

    attributes = MC(type_json, nullable=False, server_default="{}")
    expires_at = MC(DateTime(timezone=True))
    number = MC(String(16), nullable=False, unique=True)
    paid_at = MC(DateTime(timezone=True))

    order_id = MC(
        ForeignKey("order.id", ondelete="RESTRICT"), nullable=False, unique=True
    )

    order = relationship("Order", back_populates="invoice")
