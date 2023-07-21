from sqlalchemy import CheckConstraint, Column, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade


class CategoryItem(Base):
    __tablename__ = "category_item"
    __table_args__ = (
        UniqueConstraint("category_id", "article_id"),
        UniqueConstraint("category_id", "sku_id"),
        CheckConstraint("sku_id IS NOT NULL OR article_id IS NOT NULL"),
    )

    order = Column(Integer)

    category_id = Column(FKCascade("category.id"), nullable=False)
    article_id = Column(FKCascade("article.id"))
    sku_id = Column(FKCascade("sku.id"))

    category = relationship("Category", back_populates="items")
    article = relationship("Article", back_populates="category_items")
    sku = relationship("Sku", back_populates="category_items")
