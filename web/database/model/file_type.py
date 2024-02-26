from enum import IntEnum

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import Base


class FileType(Base):
    __tablename__ = "file_type"

    name = MC(String(16), nullable=False, unique=True)


class FileTypeId(IntEnum):
    IMAGE = 1
    VIDEO = 2
