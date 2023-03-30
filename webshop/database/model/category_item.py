from sqlalchemy import Column, UniqueConstraint, Integer
from sqlalchemy.orm import relationship

from webshop.database.model._utils import FKRestrict, FKCascade
from . import Base


class CategoryItem(Base):
    __tablename__ = "category_item"
    __table_args__ = (UniqueConstraint("category_id", "sku_id"),)

    order = Column(Integer)

    category_id = Column(FKCascade("category.id"), nullable=False)
    sku_id = Column(FKRestrict("sku.id"), nullable=False)

    category = relationship("Category", back_populates="items")
    sku = relationship("Sku")
