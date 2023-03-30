from enum import IntEnum

from sqlalchemy import Column, Integer, String

from . import Base


class OrderStatus(Base):
    __tablename__ = "order_status"

    name = Column(String(16), nullable=False)
    order = Column(Integer)


class OrderStatusId(IntEnum):
    PENDING = 1
    PAID = 2
    PRODUCTION = 3
    READY = 4
    COMPLETED = 5
