from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict


class Invoice(Base):
    __tablename__ = "invoice"

    attributes = Column(JSON)
    expires_at = Column(DateTime)
    number = Column(String(16), nullable=False, unique=True)
    paid_at = Column(DateTime)

    order_id = Column(FKRestrict("order.id"), nullable=False)

    order = relationship("Order", back_populates="invoices")
