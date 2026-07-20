from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import IntBase
from ._utils import default_price, val_number


class ShipmentMethod(IntBase):
    __tablename__ = "shipment_method"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    requires_billing_phone = MC(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    unit_price = MC(
        default_price,
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )
    min_days = MC(Integer, nullable=True)
    max_days = MC(Integer, nullable=True)

    class_id = MC(ForeignKey("shipment_class.id", ondelete="RESTRICT"), nullable=False)
    zone_id = MC(ForeignKey("shipment_zone.id", ondelete="RESTRICT"), nullable=False)

    class_ = relationship("ShipmentClass")
    zone = relationship("ShipmentZone")

    # Validations

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=0)
        return value

    @validates("min_days", "max_days")
    def validate_days(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=0)
        if key == "max_days" and value is not None and self.min_days is not None:
            val_number(key, value, min_=self.min_days)
        if key == "min_days" and value is not None and self.max_days is not None:
            val_number(key, value, max_=self.max_days)
        return value
