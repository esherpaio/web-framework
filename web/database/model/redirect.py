from sqlalchemy import String
from sqlalchemy.orm import mapped_column as MC

from . import Base


class Redirect(Base):
    __tablename__ = "redirect"

    url_from = MC(String(256), unique=True, nullable=False)
    url_to = MC(String(256), nullable=False)
