from enum import IntEnum

from sqlalchemy import Column, String

from . import Base


class ProductLinkType(Base):
    __tablename__ = "product_link_type"

    name = Column(String(16), nullable=False, unique=True)


class ProductLinkTypeId(IntEnum):
    UPSELL = 1
    CROSS_SELL = 2
