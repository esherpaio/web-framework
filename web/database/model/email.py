from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from ._base import Base


class Email(Base):
    __tablename__ = "email"

    data = MC(JSON, nullable=False, server_default="{}")
    event_id = MC(String(64), nullable=False)

    user_id = MC(ForeignKey("user.id", ondelete="CASCADE"))

    user = relationship("User")
