from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC

from ._base import Base
from ._utils import type_json


class AppBlueprint(Base):
    __tablename__ = "app_blueprint"

    attributes = MC(type_json, nullable=False, server_default="{}")
    css_path = MC(String(128))
    endpoint = MC(String(64), unique=True, nullable=False)
    in_sitemap = MC(Boolean, nullable=False)
    js_path = MC(String(128))
