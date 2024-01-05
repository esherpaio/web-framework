from typing import TypeVar

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column as MC


class Base(DeclarativeBase):
    id = MC(Integer, primary_key=True)
    created_at = MC(DateTime(timezone=True), server_default=func.now())
    updated_at = MC(DateTime(timezone=True), onupdate=func.now())


B = TypeVar("B", bound=Base)
