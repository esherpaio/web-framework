from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base


class Verification(Base):
    __tablename__ = "verification"

    key = MC(String(256), nullable=False)

    user_id = MC(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="verifications")

    @hybrid_property
    def is_valid(self) -> bool:
        return self.created_at + timedelta(days=1) > datetime.utcnow()
