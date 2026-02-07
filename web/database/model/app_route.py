from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column as MC

from ._base import Attribute, IntBase


class AppRoute(IntBase, Attribute):
    __tablename__ = "app_route"

    css_path = MC(String(128))
    description = MC(String(256))
    endpoint = MC(String(64), unique=True, nullable=False)
    image_url = MC(String(256))
    in_sitemap = MC(Boolean, nullable=False, default=False, server_default="false")
    js_path = MC(String(128))
    name = MC(String(64), nullable=True)
    robots = MC(String(256), nullable=True)
    is_collection = MC(Boolean, nullable=False, default=False, server_default="false")
    sitemap_query_key = MC(String(32), nullable=True)
    sitemap_query_values = MC(ARRAY(Text), nullable=True)
