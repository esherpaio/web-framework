from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade


class UserVerification(Base):
    __tablename__ = "user_verification"

    key = Column(String(256), nullable=False)

    user_id = Column(FKCascade("user.id"), nullable=False)

    user = relationship("User", back_populates="verifications")
