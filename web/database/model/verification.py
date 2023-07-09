from datetime import timedelta
import datetime
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from . import Base
from ._utils import FKCascade


class Verification(Base):
    __tablename__ = "verification"

    key = Column(String(256), nullable=False)

    user_id = Column(FKCascade("user.id"), nullable=False)

    user = relationship("User", back_populates="verifications")

    @hybrid_property
    def is_valid(self) -> bool:
        return self.created_at + timedelta(days=1) > datetime.utcnow()
