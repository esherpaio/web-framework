from typing import Any

from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKCascade
from ._validation import (
    get_slug,
)


class ProductOption(Base):
    __tablename__ = "product_option"
    __table_args__ = (UniqueConstraint("product_id", "slug"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    order = Column(Integer)
    slug = Column(String(64), nullable=False)

    product_id = Column(FKCascade("product.id"), nullable=False)

    product = relationship("Product", back_populates="options")
    values = relationship(
        "ProductValue", back_populates="option", order_by="ProductValue.order"
    )

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value
