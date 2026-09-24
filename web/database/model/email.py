from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import IntBase


class EmailType(StrEnum):
    OK = "OK"
    SPAM = "Spam"
    DUPLICATE = "Duplicate"


class Email(IntBase):
    __tablename__ = "email"

    data = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")  # type: ignore[arg-type]
    event_id = MC(String(64), nullable=False)
    scheduled_at = MC(DateTime(timezone=True))
    content_hash = MC(String(64), nullable=True)
    type = MC(
        Enum(
            EmailType,
            values_callable=lambda enum: [item.value for item in enum],
            name="email_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=EmailType.OK,
        server_default=str(EmailType.OK),
    )

    status_id = MC(
        ForeignKey("email_status.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    user_id = MC(ForeignKey("user.id", ondelete="SET NULL"))

    status = relationship("EmailStatus")
    user = relationship("User")
