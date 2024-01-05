from sqlalchemy import DateTime, String
from sqlalchemy.orm import mapped_column as MC

from . import Base


class Setting(Base):
    __tablename__ = "setting"

    banner = MC(String(256))
    cached_at = MC(DateTime(timezone=True))
