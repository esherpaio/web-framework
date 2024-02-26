from typing import Any

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Base
from ._utils import get_slug, type_json


class Category(Base):
    __tablename__ = "category"

    attributes = MC(type_json, nullable=False, server_default="{}")
    is_deleted = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False, unique=True)
    order = MC(Integer)
    slug = MC(String(64), nullable=False, unique=True)

    items = relationship(
        "CategoryItem", back_populates="category", order_by="CategoryItem.order"
    )

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value
