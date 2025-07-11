from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Base
from ._utils import default_price, val_number


class ShipmentMethod(Base):
    __tablename__ = "shipment_method"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    phone_required = MC(Boolean, nullable=False, default=False, server_default="false")
    unit_price = MC(
        default_price, nullable=False, default=Decimal("0.00"), server_default="0.00"
    )

    class_id = MC(ForeignKey("shipment_class.id", ondelete="RESTRICT"), nullable=False)
    zone_id = MC(ForeignKey("shipment_zone.id", ondelete="RESTRICT"), nullable=False)

    class_ = relationship("ShipmentClass")
    zone = relationship("ShipmentZone")

    # Validations

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=0)
        return value
