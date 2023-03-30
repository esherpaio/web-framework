from sqlalchemy import Column, String, CheckConstraint
from sqlalchemy.orm import relationship

from webshop.database.model._utils import FKCascade
from . import Base


class Access(Base):
    __tablename__ = "access"
    __table_args__ = (CheckConstraint("COALESCE(session_key, user_id) IS NOT NULL"),)

    session_key = Column(String(64), unique=True)

    user_id = Column(FKCascade("user.id"), unique=True)

    user = relationship("User", back_populates="access")
