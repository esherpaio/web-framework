from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class ArticleMedia(IntBase):
    __tablename__ = "article_media"
    __table_args__ = (UniqueConstraint("article_id", "file_id"),)

    order = MC(Integer)

    article_id = MC(ForeignKey("article.id", ondelete="CASCADE"), nullable=False)
    file_id = MC(ForeignKey("file.id", ondelete="CASCADE"), nullable=False)

    article = relationship("Article", back_populates="medias")
    file_ = relationship("File")
