from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class ShipmentZoneCountry(IntBase):
    __tablename__ = "shipment_zone_country"
    __table_args__ = (UniqueConstraint("zone_id", "country_id"),)

    zone_id = MC(ForeignKey("shipment_zone.id", ondelete="CASCADE"), nullable=False)
    country_id = MC(ForeignKey("country.id", ondelete="RESTRICT"), nullable=False)
