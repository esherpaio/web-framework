from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC

from . import Base
from ._utils import type_json


class FlaskRoute(Base):
    __tablename__ = "flask_route"

    attributes = MC(type_json, nullable=False, server_default="{}")
    description = MC(String(256))
    endpoint = MC(String(64), unique=True, nullable=False)
    image_url = MC(String(256))
    in_sitemap = MC(Boolean, nullable=False)
    name = MC(String(64), nullable=False)
    robots = MC(String(256), nullable=False)
    static_path = MC(String(128), unique=True, nullable=False)
