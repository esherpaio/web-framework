from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade, FKRestrict


class SkuDetail(Base):
    __tablename__ = "sku_detail"
    __table_args__ = (UniqueConstraint("sku_id", "value_id"),)

    sku_id = Column(FKCascade("sku.id"), nullable=False)
    option_id = Column(FKRestrict("product_option.id"), nullable=False)
    value_id = Column(FKRestrict("product_value.id"), nullable=False)

    sku = relationship("Sku", back_populates="details")
    option = relationship("ProductOption")
    value = relationship("ProductValue")
