from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from . import Base


class ShipmentZone(Base):
    __tablename__ = "shipment_zone"
    __table_args__ = (
        CheckConstraint("country_id IS NOT NULL OR region_id IS NOT NULL"),
    )

    is_deleted = MC(Boolean, nullable=False, default=False)
    order = MC(Integer)

    country_id = MC(ForeignKey("country.id", ondelete="RESTRICT"))
    region_id = MC(ForeignKey("region.id", ondelete="RESTRICT"))

    country = relationship("Country")
    region = relationship("Region")
