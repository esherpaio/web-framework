from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict, FKSetNull, price
from ._validation import set_slug


class ProductValue(Base):
    __tablename__ = "product_value"
    __table_args__ = (
        UniqueConstraint("option_id", "slug"),
        CheckConstraint("unit_price >= 0"),
    )

    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    order = Column(Integer)
    slug = Column(String(64), nullable=False)
    unit_price = Column(price, nullable=False, default=0)

    media_id = Column(FKSetNull("product_media.id"))
    option_id = Column(FKRestrict("product_option.id"), nullable=False)

    media = relationship("ProductMedia")
    option = relationship("ProductOption", back_populates="values")

    # Validations

    @set_slug("name")
    def validate_slug(self, *args) -> str:
        pass
