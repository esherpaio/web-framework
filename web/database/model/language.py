from typing import Any

from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import validates

from . import Base
from ._validation import get_lower, val_length


class Language(Base):
    __tablename__ = "language"

    code = MC(String(2), nullable=False, unique=True)
    in_sitemap = MC(Boolean, nullable=False, default=False)
    name = MC(String(64), nullable=False, unique=True)

    # Validation

    @validates("code")
    def validate_code(self, key: str, value: Any) -> Any:
        val_length(value, min_=2, max_=2)
        value = get_lower(value)
        return value
