from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import type_json
from ._validation import get_slug


class Category(Base):
    __tablename__ = "category"

    attributes = MC(type_json, nullable=False, server_default="{}")
    in_header = MC(Boolean, nullable=False, default=False)
    is_deleted = MC(Boolean, nullable=False, default=False)
    is_locked = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False, unique=True)
    order = MC(Integer)
    slug = MC(String(64), nullable=False, unique=True)

    child_id = MC(ForeignKey("category.id", ondelete="RESTRICT"))

    child = relationship("Category", remote_side="Category.id")
    items = relationship(
        "CategoryItem", back_populates="category", order_by="CategoryItem.order"
    )

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value
