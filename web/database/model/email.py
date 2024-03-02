from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base
from .email_status import EmailStatusId


class Email(Base):
    __tablename__ = "email"

    data = MC(JSON, nullable=False, server_default="{}")
    event_id = MC(String(64), nullable=False)

    status_id = MC(
        ForeignKey("email_status.id", ondelete="RESTRICT"),
        nullable=False,
        default=EmailStatusId.QUEUED,
    )
    user_id = MC(ForeignKey("user.id", ondelete="SET NULL"))

    status = relationship("EmailStatus", lazy="joined")
    user = relationship("User")
