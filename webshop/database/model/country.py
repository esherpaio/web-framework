from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict


class Country(Base):
    __tablename__ = "country"

    code = Column(String(2), nullable=False, unique=True)
    in_sitemap = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False, unique=True)

    currency_id = Column(FKRestrict("currency.id"), nullable=False)
    region_id = Column(FKRestrict("region.id"), nullable=False)

    currency = relationship("Currency")
    region = relationship("Region")
