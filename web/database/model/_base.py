from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column as MC


class Base(DeclarativeBase):
    __abstract__ = True


class IntBase(Base):
    __abstract__ = True

    id = MC(Integer, primary_key=True)
    created_at = MC(DateTime(timezone=True), server_default=func.now())
    updated_at = MC(DateTime(timezone=True), onupdate=func.now())


class StrBase(Base):
    __abstract__ = True

    id = MC(String(32), primary_key=True)
    created_at = MC(DateTime(timezone=True), server_default=func.now())
    updated_at = MC(DateTime(timezone=True), onupdate=func.now())


class Attribute(Base):
    __abstract__ = True

    attributes = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")  # type: ignore[arg-type]
