from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from webshop.database.model._utils import FKCascade
from . import Base


class UserVerification(Base):
    __tablename__ = "user_verification"

    key = Column(String(256), nullable=False)

    user_id = Column(FKCascade("user.id"), nullable=False)

    user = relationship("User", back_populates="verifications")
