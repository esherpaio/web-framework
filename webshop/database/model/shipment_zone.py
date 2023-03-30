from sqlalchemy import Column, Integer, CheckConstraint, Boolean
from sqlalchemy.orm import relationship

from . import Base
from ..utils import FKRestrict


class ShipmentZone(Base):
    __tablename__ = "shipment_zone"
    __table_args__ = (CheckConstraint("COALESCE(country_id, region_id) IS NOT NULL"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    order = Column(Integer)

    country_id = Column(FKRestrict("country.id"))
    region_id = Column(FKRestrict("region.id"))

    country = relationship("Country")
    region = relationship("Region")
