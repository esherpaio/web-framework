from sqlalchemy import Column, String

from . import Base


class Setting(Base):
    __tablename__ = "setting"

    banner = Column(String(256))
