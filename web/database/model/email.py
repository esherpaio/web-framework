from sqlalchemy import JSON, Column, String
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade


class Email(Base):
    __tablename__ = "email"

    data = Column(JSON, nullable=False, server_default="{}")
    template_id = Column(String(64), nullable=False)

    user_id = Column(FKCascade("user.id"))

    user = relationship("User")
