from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict
from ._validation import set_slug


class Category(Base):
    __tablename__ = "category"

    attributes = Column(JSON, nullable=False, server_default='{}')
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

    @set_slug("name")
    def validate_slug(self, *args) -> str:
        pass
