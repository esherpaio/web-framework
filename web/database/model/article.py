from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web.utils import none_attrgetter

from ._base import Attribute, Base
from ._utils import get_slug
from .article_media import ArticleMedia


class Article(Base, Attribute):
    __tablename__ = "article"

    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    is_visible = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    slug = MC(String(64), unique=True, nullable=False)
    summary = MC(String(256))

    route_id = MC(ForeignKey("app_route.id", ondelete="SET NULL"))

    category_items = relationship("CategoryItem", back_populates="article")
    medias = relationship(
        "ArticleMedia", back_populates="article", order_by="ArticleMedia.order"
    )
    route = relationship("AppRoute")

    # Validation

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value

    # Properties - media

    @hybrid_property
    def images(self) -> list[ArticleMedia]:
        return sorted(
            [x for x in self.medias if x.file_.is_image],
            key=none_attrgetter("order"),
        )

    @hybrid_property
    def videos(self) -> list[ArticleMedia]:
        return sorted(
            [x for x in self.medias if x.file_.is_video],
            key=none_attrgetter("order"),
        )
