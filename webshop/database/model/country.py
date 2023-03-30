from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from webshop.database.model._utils import FKRestrict
from . import Base


class Country(Base):
    __tablename__ = "country"

    code = Column(String(2), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)

    currency_id = Column(FKRestrict("currency.id"), nullable=False)
    region_id = Column(FKRestrict("region.id"), nullable=False)

    currency = relationship("Currency")
    region = relationship("Region")
