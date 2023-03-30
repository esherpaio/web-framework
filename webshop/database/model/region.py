from sqlalchemy import Column, String, Boolean

from . import Base


class Region(Base):
    __tablename__ = "region"

    is_europe = Column(Boolean, nullable=False)
    name = Column(String(64), nullable=False, unique=True)
