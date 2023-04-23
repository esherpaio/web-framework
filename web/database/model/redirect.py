from sqlalchemy import Column, String

from . import Base


class Redirect(Base):
    __tablename__ = "redirect"

    url_from = Column(String(256), unique=True, nullable=False)
    url_to = Column(String(256), nullable=False)
