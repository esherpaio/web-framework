from sqlalchemy import Column, String

from . import Base


class Language(Base):
    __tablename__ = "language"

    code = Column(String(2), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)
