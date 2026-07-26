from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class VerificationType(StrEnum):
    VERIFICATION = "verification"
    PASSWORD = "password"
    REVIEW = "review"


class Verification(IntBase):
    __tablename__ = "verification"

    key = MC(String(256), nullable=False)
    type = MC(String(32), nullable=True)
    valid_from = MC(DateTime(timezone=True))
    expires_at = MC(DateTime(timezone=True))
    data = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")  # type: ignore[arg-type]

    user_id = MC(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="verifications")

    @property
    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.valid_from is not None and self.valid_from > now:
            return False
        if self.expires_at is not None and self.expires_at < now:
            return False
        return True
