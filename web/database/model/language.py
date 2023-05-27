from sqlalchemy import Boolean, Column, String

from . import Base


class Language(Base):
    __tablename__ = "language"

    code = Column(String(2), nullable=False, unique=True)
    in_sitemap = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False, unique=True)
