from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ..utils import FKCascade


class ProductMedia(Base):
    __tablename__ = "product_media"
    __table_args__ = (UniqueConstraint("file_id", "product_id"),)

    order = Column(Integer)

    file_id = Column(FKCascade("file.id"), nullable=False)
    product_id = Column(FKCascade("product.id"), nullable=False)

    file = relationship("File")
    product = relationship("Product", back_populates="medias")
