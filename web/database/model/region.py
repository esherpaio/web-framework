from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class Region(IntBase):
    __tablename__ = "region"

    name = MC(String(64), nullable=False, unique=True)
