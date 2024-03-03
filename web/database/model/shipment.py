from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Attribute, Base


class Shipment(Base, Attribute):
    __tablename__ = "shipment"
    __table_args__ = (UniqueConstraint("url", "order_id"),)

    carrier = MC(String(64))
    code = MC(String(64))
    url = MC(String(256), nullable=False)

    order_id = MC(ForeignKey("order.id", ondelete="RESTRICT"), nullable=False)

    order = relationship("Order", back_populates="shipments")
