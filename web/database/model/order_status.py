from enum import IntEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class OrderStatus(IntBase):
    __tablename__ = "order_status"

    name = MC(String(16), nullable=False)
    order = MC(Integer)


class OrderStatusId(IntEnum):
    PENDING = 1
    PAID = 2
    IN_PROGRESS = 3
    READY = 4
    COMPLETED = 5
