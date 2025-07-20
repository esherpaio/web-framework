from enum import StrEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import StrBase


class EmailStatus(StrBase):
    __tablename__ = "email_status"

    name = MC(String(16), nullable=False)
    order = MC(Integer)


class EmailStatusId(StrEnum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
