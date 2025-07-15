from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Attribute, IntBase
from ._utils import get_slug


class Category(IntBase, Attribute):
    __tablename__ = "category"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False, unique=True)
    order = MC(Integer)
    slug = MC(String(64), nullable=False, unique=True)

    route_id = MC(ForeignKey("app_route.id", ondelete="SET NULL"))

    items = relationship(
        "CategoryItem", back_populates="category", order_by="CategoryItem.order"
    )
    route = relationship("AppRoute")

    # Validations

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value
