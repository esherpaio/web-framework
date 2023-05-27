from sqlalchemy import Boolean, CheckConstraint, Column, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict, price


class ShipmentMethod(Base):
    __tablename__ = "shipment_method"
    __table_args__ = (CheckConstraint("unit_price >= 0"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    phone_required = Column(Boolean, nullable=False, default=False)
    unit_price = Column(price, nullable=False, default=0)

    class_id = Column(FKRestrict("shipment_class.id"), nullable=False)
    zone_id = Column(FKRestrict("shipment_zone.id"), nullable=False)

    class_ = relationship("ShipmentClass")
    zone = relationship("ShipmentZone")

    def __lt__(self, other: "ShipmentMethod") -> bool:
        return self.unit_price < other.unit_price
