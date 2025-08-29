from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class FileType(StrBase):
    __tablename__ = "file_type"

    name = MC(String(16), nullable=False, unique=True)


class FileTypeId(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
