from enum import IntEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from . import Base


class OrderStatus(Base):
    __tablename__ = "order_status"

    name = MC(String(16), nullable=False)
    order = MC(Integer)


class OrderStatusId(IntEnum):
    PENDING = 1
    PAID = 2
    PRODUCTION = 3
    READY = 4
    COMPLETED = 5
