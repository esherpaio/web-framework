from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import validates

from ._base import IntBase
from ._utils import val_number


class AppSettings(IntBase):
    __tablename__ = "app_settings"

    automator = MC(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")
    banner = MC(String(256))
    cached_at = MC(DateTime(timezone=True))
    css_path = MC(String(128))
    js_path = MC(String(128))
    handling_min_days = MC(Integer, nullable=True)
    handling_max_days = MC(Integer, nullable=True)

    @validates("handling_min_days", "handling_max_days")
    def validate_handling_days(self, key: str, value: int | None) -> int | None:
        val_number(key, value, min_=0)
        return value
