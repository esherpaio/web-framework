from enum import StrEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class ReviewStatus(StrBase):
    __tablename__ = "review_status"

    name = MC(String(16), nullable=False)
    order = MC(Integer)


class ReviewStatusId(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
