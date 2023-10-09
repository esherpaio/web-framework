from sqlalchemy import JSON, Column, String, UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict


class Shipment(Base):
    __tablename__ = "shipment"
    __table_args__ = (UniqueConstraint("url", "order_id"),)

    attributes = Column(
        MutableDict.as_mutable(JSON), nullable=False, server_default="{}"
    )
    url = Column(String(256), nullable=False)

    order_id = Column(FKRestrict("order.id"), nullable=False)

    order = relationship("Order", back_populates="shipments")
