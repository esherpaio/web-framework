from enum import IntEnum

from sqlalchemy import Column, String

from . import Base


class ProductType(Base):
    __tablename__ = "product_type"

    name = Column(String(16), nullable=False, unique=True)


class ProductTypeId(IntEnum):
    PHYSICAL = 1
