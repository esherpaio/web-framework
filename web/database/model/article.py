from typing import Any

from sqlalchemy import JSON, Boolean, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from web.helper.objects import none_aware_attrgetter

from . import Base
from ._validation import get_slug
from .article_media import ArticleMedia


class Article(Base):
    __tablename__ = "article"

    attributes = Column(JSON, nullable=False, server_default="{}")
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    slug = Column(String(64), unique=True, nullable=False)
    summary = Column(String(64))

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
            key=none_aware_attrgetter("order"),
        )

    @hybrid_property
    def videos(self) -> list[ArticleMedia]:
        return sorted(
            [x for x in self.medias if x.file.is_video],
            key=none_aware_attrgetter("order"),
        )
