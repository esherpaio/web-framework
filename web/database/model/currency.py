from decimal import Decimal
from enum import IntEnum
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import validates

from ._base import IntBase
from ._utils import default_rate, get_upper, val_length, val_number


class Currency(IntBase):
    __tablename__ = "currency"

    code = MC(String(3), nullable=False, unique=True)
    rate = MC(default_rate, nullable=False, default=Decimal("1"), server_default="1")
    symbol = MC(String(3), nullable=False)

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(key, value, min_=3, max_=3)
        value = get_upper(value)
        return value

    @validates("rate")
    def validate_rate(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=0)
        return value


class CurrencyId(IntEnum):
    EUR = 1
    USD = 2
