from typing import Any

from sqlalchemy import Boolean, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web.libs.utils import none_attrgetter

from ._base import Base
from ._utils import get_slug, type_json
from .article_media import ArticleMedia


class Article(Base):
    __tablename__ = "article"

    attributes = MC(type_json, nullable=False, server_default="{}")
    is_deleted = MC(Boolean, nullable=False, default=False)
    is_visible = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False)
    slug = MC(String(64), unique=True, nullable=False)
    summary = MC(String(64))

    category_items = relationship("CategoryItem", back_populates="article")
    medias = relationship(
        "ArticleMedia", back_populates="article", order_by="ArticleMedia.order"
    )

    # Validation

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value

    # Properties - media

    @hybrid_property
    def images(self) -> list[ArticleMedia]:
        return sorted(
            [x for x in self.medias if x.file.is_image],
            key=none_attrgetter("order"),
        )

    @hybrid_property
    def videos(self) -> list[ArticleMedia]:
        return sorted(
            [x for x in self.medias if x.file.is_video],
            key=none_attrgetter("order"),
        )
