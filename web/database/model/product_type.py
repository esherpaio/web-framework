from enum import IntEnum

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import Base


class ProductType(Base):
    __tablename__ = "product_type"

    name = MC(String(16), nullable=False, unique=True)


class ProductTypeId(IntEnum):
    PHYSICAL = 1
