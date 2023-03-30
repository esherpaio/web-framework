from sqlalchemy import Column, String, Boolean, UniqueConstraint, Integer
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade
from ._validation import set_slug


class ProductOption(Base):
    __tablename__ = "product_option"
    __table_args__ = (UniqueConstraint("product_id", "slug"),)

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    order = Column(Integer)
    slug = Column(String(64), nullable=False)

    product_id = Column(FKCascade("product.id"), nullable=False)

    product = relationship("Product", back_populates="options")
    values = relationship("ProductValue", back_populates="option")

    # Validations

    @set_slug("name")
    def validate_slug(self, *args) -> str:
        pass
