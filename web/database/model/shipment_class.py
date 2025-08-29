from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class ShipmentClass(IntBase):
    __tablename__ = "shipment_class"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    order = MC(Integer)
