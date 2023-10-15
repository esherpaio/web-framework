from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from . import Base
from .product_link_type import ProductLinkTypeId


class ProductLink(Base):
    __tablename__ = "product_link"
    __table_args__ = (UniqueConstraint("product_id", "sku_id", "type_id"),)

    product_id = MC(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    sku_id = MC(ForeignKey("sku.id", ondelete="CASCADE"), nullable=False)
    type_id = MC(
        ForeignKey("product_link_type.id", ondelete="RESTRICT"), nullable=False
    )

    product = relationship("Product")
    sku = relationship("Sku")
    type = relationship("ProductLinkType")

    # Properties - types

    @hybrid_property
    def is_upsell(self) -> bool:
        return self.type_id == ProductLinkTypeId.UPSELL

    @hybrid_property
    def is_cross_sell(self) -> bool:
        return self.type_id == ProductLinkTypeId.CROSS_SELL
