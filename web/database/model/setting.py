from sqlalchemy import Column, DateTime, String

from . import Base


class Setting(Base):
    __tablename__ = "setting"

    banner = Column(String(256))
    cached_at = Column(DateTime)
