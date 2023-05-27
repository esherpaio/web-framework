from sqlalchemy import Boolean, Column, Integer, String

from . import Base


class ShipmentClass(Base):
    __tablename__ = "shipment_class"

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    order = Column(Integer)
