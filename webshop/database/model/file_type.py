from enum import IntEnum

from sqlalchemy import Column, String

from . import Base


class FileType(Base):
    __tablename__ = "file_type"

    name = Column(String(16), nullable=False, unique=True)


class FileTypeId(IntEnum):
    IMAGE = 1
    VIDEO = 2
