from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict


class Shipment(Base):
    __tablename__ = "shipment"

    url = Column(String(256), nullable=False)

    order_id = Column(FKRestrict("order.id"), nullable=False)

    order = relationship("Order", back_populates="shipments")
