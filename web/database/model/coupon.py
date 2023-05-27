from sqlalchemy import Boolean, CheckConstraint, Column, String
from sqlalchemy.ext.hybrid import hybrid_property

from . import Base
from ._utils import price, rate


class Coupon(Base):
    __tablename__ = "coupon"
    __table_args__ = (CheckConstraint("amount IS NULL OR rate IS NULL"),)

    amount = Column(price)
    code = Column(String(16), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    rate = Column(rate)

    # Properties - general

    @hybrid_property
    def percentage(self) -> int | None:
        if self.rate:
            return round(abs((self.rate * 100) - 100))
