from sqlalchemy import CheckConstraint, Column, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade


class Access(Base):
    __tablename__ = "access"
    __table_args__ = (CheckConstraint("session_key IS NULL OR user_id IS NULL"),)

    session_key = Column(String(64), unique=True)

    user_id = Column(FKCascade("user.id"), unique=True)

    user = relationship("User", back_populates="access")
