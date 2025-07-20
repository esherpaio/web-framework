from enum import StrEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class OrderStatus(StrBase):
    __tablename__ = "order_status"

    name = MC(String(16), nullable=False)
    order = MC(Integer)


class OrderStatusId(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    IN_PROGRESS = "in-progress"
    READY = "ready"
    COMPLETED = "completed"
