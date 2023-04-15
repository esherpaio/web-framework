from sqlalchemy import Column, DateTime, String

from . import Base


class Invoice(Base):
    __tablename__ = "invoice"

    expires_at = Column(DateTime)
    number = Column(String(16), nullable=False, unique=True)
    paid_at = Column(DateTime)
