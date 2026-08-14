from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class SitemapImage(IntBase):
    __tablename__ = "sitemap_image"
    __table_args__ = (UniqueConstraint("location_id", "loc"),)

    loc = MC(String(2048), nullable=False)

    location_id = MC(
        ForeignKey("sitemap_location.id", ondelete="CASCADE"),
        nullable=False,
    )

    location = relationship("SitemapLocation", back_populates="images")
