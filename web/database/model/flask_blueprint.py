from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC

from . import Base
from ._utils import type_json


class FlaskBlueprint(Base):
    __tablename__ = "flask_blueprint"

    attributes = MC(type_json, nullable=False, server_default="{}")
    endpoint = MC(String(64), unique=True, nullable=False)
    in_sitemap = MC(Boolean, nullable=False)
    static_path = MC(String(128))
