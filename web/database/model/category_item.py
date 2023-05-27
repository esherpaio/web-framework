from sqlalchemy import CheckConstraint, Column, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade, FKRestrict


class CategoryItem(Base):
    __tablename__ = "category_item"
    __table_args__ = (
        CheckConstraint("sku_id IS NULL OR article_id IS NULL"),
        UniqueConstraint("category_id", "article_id"),
        UniqueConstraint("category_id", "sku_id"),
    )

    order = Column(Integer)

    article_id = Column(FKRestrict("article.id"))
    category_id = Column(FKCascade("category.id"), nullable=False)
    sku_id = Column(FKRestrict("sku.id"))

    article = relationship("Article")
    category = relationship("Category", back_populates="items")
    sku = relationship("Sku")
