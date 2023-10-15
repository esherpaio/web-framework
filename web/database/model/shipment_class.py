from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column as MC

from . import Base


class ShipmentClass(Base):
    __tablename__ = "shipment_class"

    is_deleted = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False)
    order = MC(Integer)
