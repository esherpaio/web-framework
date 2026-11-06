from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class ShipmentZone(IntBase):
    __tablename__ = "shipment_zone"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    order = MC(Integer)

    countries = relationship(
        "Country",
        secondary="shipment_zone_country",
        lazy="selectin",
        order_by="Country.name",
    )
