from sqlalchemy import DateTime, String
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class AppSettings(IntBase):
    __tablename__ = "app_settings"

    banner = MC(String(256))
    cached_at = MC(DateTime(timezone=True))
    css_path = MC(String(128))
    js_path = MC(String(128))
