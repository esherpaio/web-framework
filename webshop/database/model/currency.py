from enum import IntEnum

from sqlalchemy import Column, String

from webshop.database.model._utils import rate
from . import Base


class Currency(Base):
    __tablename__ = "currency"

    code = Column(String(3), nullable=False, unique=True)
    rate = Column(rate, nullable=False, default=1)
    symbol = Column(String(3), nullable=False)


class CurrencyId(IntEnum):
    EUR = 1
    USD = 2
