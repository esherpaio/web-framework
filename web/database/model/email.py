from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base
from .email_status import EmailStatusId


class Email(Base):
    __tablename__ = "email"

    data = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")  # type: ignore[arg-type]
    event_id = MC(String(64), nullable=False)

    status_id = MC(
        ForeignKey("email_status.id", ondelete="RESTRICT"),
        nullable=False,
        default=EmailStatusId.QUEUED,
        server_default=str(EmailStatusId.QUEUED),
    )
    user_id = MC(ForeignKey("user.id", ondelete="SET NULL"))

    status = relationship("EmailStatus")
    user = relationship("User")
