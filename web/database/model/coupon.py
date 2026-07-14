from typing import Any

from sqlalchemy import Boolean, CheckConstraint, Index, String, event, text, update
from sqlalchemy.engine import Connection
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapper, validates
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase
from ._utils import default_price, default_rate, get_upper, val_length, val_number


class Coupon(IntBase):
    __tablename__ = "coupon"
    __table_args__ = (
        CheckConstraint("amount IS NULL OR rate IS NULL"),
        Index(None, "is_default", unique=True, postgresql_where=text("is_default")),
    )

    amount = MC(default_price)
    code = MC(String(32), nullable=False)
    is_default = MC(Boolean, nullable=False, default=False, server_default="false")
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
        if self.rate is not None:
            return int(round((self.rate - 1) * 100))
        return None

    @hybrid_property
    def discount_percentage(self) -> int | None:
        if self.rate is not None:
            return int(round((1 - self.rate) * 100))
        return None


@event.listens_for(Coupon, "before_insert")
@event.listens_for(Coupon, "before_update")
def _unset_other_defaults(
    mapper: Mapper,
    connection: Connection,
    target: Coupon,
) -> None:
    if not target.is_default:
        return
    query = update(Coupon).where(Coupon.is_default.is_(True)).values(is_default=False)
    if target.id is not None:
        query = query.where(Coupon.id != target.id)
    connection.execute(query)
