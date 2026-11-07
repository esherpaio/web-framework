from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class ProductLink(IntBase):
    __tablename__ = "product_link"
    __table_args__ = (UniqueConstraint("product_id", "sku_id", "type_id"),)

    product_id = MC(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    sku_id = MC(ForeignKey("sku.id", ondelete="CASCADE"), nullable=False)
    type_id = MC(
        ForeignKey("product_link_type.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    product = relationship("Product")
    sku = relationship("Sku")
    type_ = relationship("ProductLinkType")
