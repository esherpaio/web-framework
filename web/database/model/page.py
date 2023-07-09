from sqlalchemy import JSON, Boolean, Column, String

from . import Base


class Page(Base):
    __tablename__ = "page"

    attributes = Column(JSON)
    desc = Column(String(256))
    endpoint = Column(String(64), unique=True, nullable=False)
    in_sitemap = Column(Boolean, nullable=False)
    name = Column(String(64), nullable=False)
    robots = Column(String(256), nullable=False)
    img_url = Column(String(256))
