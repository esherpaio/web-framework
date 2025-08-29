from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Attribute, IntBase


class Shipment(IntBase, Attribute):
    __tablename__ = "shipment"

    carrier = MC(String(64))
    code = MC(String(64))
    url = MC(String(256), nullable=False)

    order_id = MC(ForeignKey("order.id", ondelete="RESTRICT"), nullable=False)

    order = relationship("Order", back_populates="shipments")
