from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade


class ProductMedia(Base):
    __tablename__ = "product_media"
    __table_args__ = (UniqueConstraint("product_id", "file_id"),)

    order = Column(Integer)

    product_id = Column(FKCascade("product.id"), nullable=False)
    file_id = Column(FKCascade("file.id"), nullable=False)

    product = relationship("Product", back_populates="medias")
    file = relationship("File")
