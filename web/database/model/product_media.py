from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base


class ProductMedia(Base):
    __tablename__ = "product_media"
    __table_args__ = (UniqueConstraint("product_id", "file_id"),)

    order = MC(Integer)

    product_id = MC(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    file_id = MC(ForeignKey("file.id", ondelete="CASCADE"), nullable=False)

    product = relationship("Product", back_populates="medias")
    file_ = relationship("File")
