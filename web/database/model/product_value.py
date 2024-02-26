from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Base
from ._utils import default_price, get_slug, val_number


class ProductValue(Base):
    __tablename__ = "product_value"
    __table_args__ = (UniqueConstraint("option_id", "slug"),)

    is_deleted = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False)
    order = MC(Integer)
    slug = MC(String(64), nullable=False)
    unit_price = MC(default_price, nullable=False, default=0)

    media_id = MC(ForeignKey("product_media.id", ondelete="SET NULL"))
    option_id = MC(ForeignKey("product_option.id", ondelete="CASCADE"), nullable=False)

    media = relationship("ProductMedia")
    option = relationship("ProductOption", back_populates="values")

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value
