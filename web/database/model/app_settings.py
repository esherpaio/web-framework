from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column as MC

from ._base import IntBase


class AppSettings(IntBase):
    __tablename__ = "app_settings"

    automator = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")
    banner = MC(String(256))
    cached_at = MC(DateTime(timezone=True))
    css_path = MC(String(128))
    js_path = MC(String(128))
