from enum import StrEnum

from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Attribute, IntBase


class SitemapImageMode(StrEnum):
    COMBINED = "combined"
    SEPARATE = "separate"


class AppRoute(IntBase, Attribute):
    __tablename__ = "app_route"

    css_path = MC(String(128))
    description = MC(String(256))
    endpoint = MC(String(64), unique=True, nullable=False)
    image_url = MC(String(256))
    image_url_alt = MC(String(256))
    in_sitemap = MC(Boolean, nullable=False, default=False, server_default="false")
    js_path = MC(String(128))
    name = MC(String(64), nullable=True)
    breadcrumb_name = MC(String(64), nullable=True)
    robots = MC(String(256), nullable=True)
    is_collection = MC(Boolean, nullable=False, default=False, server_default="false")
    sitemap_group = MC(
        String(32),
        nullable=False,
        default="pages",
        server_default="pages",
    )
    sitemap_image_mode = MC(String(16), nullable=True)
    template_path = MC(String(128), nullable=True)

    sitemap_locations = relationship(
        "SitemapLocation",
        back_populates="route",
        cascade="all, delete-orphan",
    )
