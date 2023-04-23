from sqlalchemy import Column, String

from . import Base
from ._validation import check_slug


class Redirect(Base):
    __tablename__ = "redirect"

    slug_from = Column(String(256), unique=True, nullable=False)
    slug_to = Column(String(256), nullable=False)

    # Validation

    @check_slug("slug_from", "slug_to")
    def validate_slug(self, *args) -> str:
        pass
