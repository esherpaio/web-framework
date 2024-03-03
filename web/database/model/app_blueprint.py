from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC

from ._base import Attribute, Base


class AppBlueprint(Base, Attribute):
    __tablename__ = "app_blueprint"

    css_path = MC(String(128))
    endpoint = MC(String(64), unique=True, nullable=False)
    in_sitemap = MC(Boolean, nullable=False)
    js_path = MC(String(128))
