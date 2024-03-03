from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column as MC


class Base(DeclarativeBase):
    id = MC(Integer, primary_key=True)
    created_at = MC(DateTime(), server_default=func.now())
    updated_at = MC(DateTime(), onupdate=func.now())


class Attribute(DeclarativeBase):
    attributes = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")  # type: ignore[arg-type]
