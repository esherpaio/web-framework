from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC

from . import Base
from ._utils import type_json


class Page(Base):
    __tablename__ = "page"

    attributes = MC(type_json, nullable=False, server_default="{}")
    description = MC(String(256))
    endpoint = MC(String(64), unique=True, nullable=False)
    in_sitemap = MC(Boolean, nullable=False)
    name = MC(String(64), nullable=False)
    robots = MC(String(256), nullable=False)
    image_url = MC(String(256))
