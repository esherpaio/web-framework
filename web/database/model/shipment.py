from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base
from ._utils import type_json


class Shipment(Base):
    __tablename__ = "shipment"
    __table_args__ = (UniqueConstraint("url", "order_id"),)

    attributes = MC(type_json, nullable=False, server_default="{}")
    carrier = MC(String(64))
    code = MC(String(64))
    url = MC(String(256), nullable=False)

    order_id = MC(ForeignKey("order.id", ondelete="RESTRICT"), nullable=False)

    order = relationship("Order", back_populates="shipments")
