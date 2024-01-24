from sqlalchemy import DateTime, String
from sqlalchemy.orm import mapped_column as MC

from . import Base


class AppSetting(Base):
    __tablename__ = "app_setting"

    banner = MC(String(256))
    cached_at = MC(DateTime())
    css_path = MC(String(128))
    js_path = MC(String(128))
