from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ..utils import FKRestrict, FKCascade


class SkuDetail(Base):
    __tablename__ = "sku_detail"
    __table_args__ = (UniqueConstraint("sku_id", "value_id"),)

    option_id = Column(FKRestrict("product_option.id"), nullable=False)
    sku_id = Column(FKCascade("sku.id"), nullable=False)
    value_id = Column(FKRestrict("product_value.id"), nullable=False)

    option = relationship("ProductOption")
    sku = relationship("Sku", back_populates="details")
    value = relationship("ProductValue")
