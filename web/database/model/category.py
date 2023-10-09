from typing import Any

from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKRestrict
from ._validation import (
    get_slug,
)


class Category(Base):
    __tablename__ = "category"

    attributes = Column(
        MutableDict.as_mutable(JSON), nullable=False, server_default="{}"
    )
    in_header = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False, unique=True)
    order = Column(Integer)
    slug = Column(String(64), nullable=False, unique=True)

    child_id = Column(FKRestrict("category.id"))

    child = relationship("Category", remote_side="Category.id")
    items = relationship(
        "CategoryItem", back_populates="category", order_by="CategoryItem.order"
    )

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value
