from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade


class ArticleMedia(Base):
    __tablename__ = "article_media"
    __table_args__ = (UniqueConstraint("article_id", "file_id"),)

    order = Column(Integer)

    article_id = Column(FKCascade("article.id"), nullable=False)
    file_id = Column(FKCascade("file.id"), nullable=False)

    article = relationship("Article", back_populates="medias")
    file = relationship("File")
