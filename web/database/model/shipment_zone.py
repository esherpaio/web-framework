from sqlalchemy import Boolean, CheckConstraint, Column, Integer
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict


class ShipmentZone(Base):
    __tablename__ = "shipment_zone"
    __table_args__ = (CheckConstraint("country_id IS NULL OR region_id IS NULL"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    order = Column(Integer)

    country_id = Column(FKRestrict("country.id"))
    region_id = Column(FKRestrict("region.id"))

    country = relationship("Country")
    region = relationship("Region")
