from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import IntBase
from ._utils import get_slug


class ProductOption(IntBase):
    __tablename__ = "product_option"
    __table_args__ = (UniqueConstraint("product_id", "slug"),)

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    order = MC(Integer)
    slug = MC(String(64), nullable=False)

    product_id = MC(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)

    product = relationship("Product", back_populates="options")
    values = relationship(
        "ProductValue", back_populates="option", order_by="ProductValue.order"
    )

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value
