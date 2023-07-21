from typing import Any

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import validates

from . import Base
from ._validation import get_upper, val_length


class Language(Base):
    __tablename__ = "language"

    code = Column(String(2), nullable=False, unique=True)
    in_sitemap = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False, unique=True)

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(value, min_=2, max_=2)
        value = get_upper(value)
        return value
