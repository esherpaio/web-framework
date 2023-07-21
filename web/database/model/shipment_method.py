from typing import Any

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKRestrict, default_price
from ._validation import val_number


class ShipmentMethod(Base):
    __tablename__ = "shipment_method"

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    phone_required = Column(Boolean, nullable=False, default=False)
    unit_price = Column(default_price, nullable=False, default=0)

    class_id = Column(FKRestrict("shipment_class.id"), nullable=False)
    zone_id = Column(FKRestrict("shipment_zone.id"), nullable=False)

    class_ = relationship("ShipmentClass")
    zone = relationship("ShipmentZone")

    # Validations

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value
