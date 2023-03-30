from sqlalchemy import Column, String, Boolean, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from . import Base
from ..utils import price, rate


class Coupon(Base):
    __tablename__ = "coupon"
    __table_args__ = (CheckConstraint("COALESCE(amount, rate) IS NOT NULL"),)

    amount = Column(price)
    code = Column(String(16), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    rate = Column(rate)

    # Properties - general

    @hybrid_property
    def percentage(self) -> int | None:
        if self.rate:
            return round(abs((self.rate * 100) - 100))
