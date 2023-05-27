from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from web.helper.operator import none_aware_attrgetter

from . import Base
from ._validation import set_slug
from .article_media import ArticleMedia


class Article(Base):
    __tablename__ = "article"

    html = Column(Text)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    slug = Column(String(64), unique=True, nullable=False)
    summary = Column(String(64))

    medias = relationship("ArticleMedia", back_populates="article")

    # Validation

    @set_slug("name")
    def validate_slug(self, *args) -> str:
        pass

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
