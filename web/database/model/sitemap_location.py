from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class SitemapLocation(IntBase):
    __tablename__ = "sitemap_location"
    __table_args__ = (UniqueConstraint("route_id", "endpoint_args"),)

    endpoint_args = MC(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        default=dict,
        server_default="{}",
    )
    lastmod = MC(DateTime(timezone=True), nullable=False)
    template_hash = MC(String(64), nullable=True)

    route_id = MC(ForeignKey("app_route.id", ondelete="CASCADE"), nullable=False)
    images = relationship(
        "SitemapImage",
        back_populates="location",
        cascade="all, delete-orphan",
        order_by="SitemapImage.loc",
    )
    route = relationship("AppRoute", back_populates="sitemap_locations")
