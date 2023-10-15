from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship

from . import Base


class Email(Base):
    __tablename__ = "email"

    data = MC(JSON, nullable=False, server_default="{}")
    template_id = MC(String(64), nullable=False)

    user_id = MC(ForeignKey("user.id", ondelete="CASCADE"))

    user = relationship("User")
