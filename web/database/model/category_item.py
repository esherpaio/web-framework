from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from . import Base


class CategoryItem(Base):
    __tablename__ = "category_item"
    __table_args__ = (
        UniqueConstraint("category_id", "article_id"),
        UniqueConstraint("category_id", "sku_id"),
        CheckConstraint("sku_id IS NOT NULL OR article_id IS NOT NULL"),
    )

    order = MC(Integer)

    category_id = MC(ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    article_id = MC(ForeignKey("article.id", ondelete="CASCADE"))
    sku_id = MC(ForeignKey("sku.id", ondelete="CASCADE"))

    category = relationship("Category", back_populates="items")
    article = relationship("Article", back_populates="category_items")
    sku = relationship("Sku", back_populates="category_items")
