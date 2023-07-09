from enum import IntEnum

from sqlalchemy import Column, String

from . import Base
from ._utils import default_rate


class Currency(Base):
    __tablename__ = "currency"

    code = Column(String(3), nullable=False, unique=True)
    rate = Column(default_rate, nullable=False, default=1)
    symbol = Column(String(3), nullable=False)


class CurrencyId(IntEnum):
    EUR = 1
    USD = 2
