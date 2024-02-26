from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base


class SkuDetail(Base):
    __tablename__ = "sku_detail"
    __table_args__ = (UniqueConstraint("sku_id", "value_id"),)

    sku_id = MC(ForeignKey("sku.id", ondelete="CASCADE"), nullable=False)
    option_id = MC(ForeignKey("product_option.id", ondelete="RESTRICT"), nullable=False)
    value_id = MC(ForeignKey("product_value.id", ondelete="RESTRICT"), nullable=False)

    sku = relationship("Sku", back_populates="details")
    option = relationship("ProductOption")
    value = relationship("ProductValue")
