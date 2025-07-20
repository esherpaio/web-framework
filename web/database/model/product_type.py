from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class ProductType(StrBase):
    __tablename__ = "product_type"

    name = MC(String(16), nullable=False, unique=True)


class ProductTypeId(StrEnum):
    PHYSICAL = "physical"
