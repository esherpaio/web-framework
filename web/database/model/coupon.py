from typing import Any

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import validates

from ._base import IntBase
from ._utils import default_price, default_rate, get_upper, val_length, val_number


class Coupon(IntBase):
    __tablename__ = "coupon"
    __table_args__ = (CheckConstraint("amount IS NULL OR rate IS NULL"),)

    amount = MC(default_price)
    code = MC(String(32), nullable=False)
    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    rate = MC(default_rate)

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(key, value, min_=2)
        value = get_upper(value)
        return value

    @validates("rate")
    def validate_rate(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=0, max_=1)
        return value

    # Properties - general

    @hybrid_property
    def percentage(self) -> int | None:
        if self.rate:
            return int(round((self.rate - 1) * 100))
        return None
