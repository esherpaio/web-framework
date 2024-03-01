from enum import IntEnum

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column as MC

from ._base import Base


class EmailStatus(Base):
    __tablename__ = "email_status"

    name = MC(String(16), nullable=False)
    order = MC(Integer)


class EmailStatusId(IntEnum):
    QUEUED = 1
    SENT = 2
    FAILED = 3
