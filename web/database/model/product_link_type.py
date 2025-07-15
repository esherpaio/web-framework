from enum import IntEnum

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class ProductLinkType(IntBase):
    __tablename__ = "product_link_type"

    name = MC(String(16), nullable=False, unique=True)


class ProductLinkTypeId(IntEnum):
    UPSELL = 1
    CROSS_SELL = 2
