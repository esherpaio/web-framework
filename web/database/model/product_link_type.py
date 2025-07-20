from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class ProductLinkType(StrBase):
    __tablename__ = "product_link_type"

    name = MC(String(16), nullable=False, unique=True)


class ProductLinkTypeId(StrEnum):
    UPSELL = "upsell"
    CROSS_SELL = "cross-sell"
