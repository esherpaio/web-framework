import json
import os
from functools import cached_property
from typing import Any

from dotenv import load_dotenv

from web.utils import Singleton

#
# Types
#


class StaticVar:
    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value


class EnvVar:
    def __init__(self, key: str, type_: Any, default: Any = None) -> None:
        self.key = key
        self.type_ = type_
        self.default = default

    @cached_property
    def value(self) -> Any:
        return self.parse(os.getenv(self.key, self.default))

    def parse(self, value: str) -> Any:
        if self.type_ is str:
            return value
        if self.type_ is int:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        if self.type_ is bool:
            return value in ["true", "1"]


class ConfigVar:
    def __init__(self, key: str, default: Any = None) -> None:
        self.key = key
        self.default = default

    @cached_property
    def value(self) -> Any:
        path = EnvVar("APP_CONFIG", str).value
        if path is None or not os.path.isfile(path):
            raise EnvironmentError
        with open(path, "r") as file_:
            data = json.loads(file_.read())
        return data.get(self.key, self.default)


#
# Base
#


class Config(metaclass=Singleton):
    VARS: list[EnvVar | ConfigVar | StaticVar] = [
        # App configuration
        StaticVar("APP_ROOT", os.path.dirname(os.path.abspath(__file__))),
        EnvVar("APP_LOG_LEVEL", str, default="INFO"),
        EnvVar("APP_DEBUG", bool, default=False),
        EnvVar("APP_DEBUG_PORT", int, default=5000),
        EnvVar("APP_URL_SCHEME", str, default="https"),
        EnvVar("APP_OPTIMIZE", bool, default=True),
        EnvVar("APP_SYNC_EXTERNAL", bool, default=False),
        EnvVar("APP_SYNC_STATIC", bool, default=True),
        EnvVar("APP_SYNC_TIMEOUT", int, default=10),
        # Worker
        EnvVar("WORKER_ENABLED", bool, default=False),
        EnvVar("WORKER_INTERVAL_S", int, default=300),
        # Auth
        EnvVar("AUTH_JWT_SECRET", str),
        EnvVar("AUTH_JWT_EXPIRES_S", int, default=86400),
        EnvVar("AUTH_JWT_ALLOW_GUEST", bool, default=False),
        EnvVar("AUTH_JWT_DECODE_LEEWAY_S", int, default=0),
        # Business details
        ConfigVar("BUSINESS_NAME"),
        ConfigVar("BUSINESS_EMAIL"),
        ConfigVar("BUSINESS_CC"),
        ConfigVar("BUSINESS_VAT"),
        ConfigVar("BUSINESS_VAT_RATE"),
        ConfigVar("BUSINESS_VAT_REVERSE_CHARGE"),
        ConfigVar("BUSINESS_STREET"),
        ConfigVar("BUSINESS_CITY"),
        ConfigVar("BUSINESS_ZIP_CODE"),
        ConfigVar("BUSINESS_COUNTRY"),
        ConfigVar("BUSINESS_COUNTRY_CODE"),
        # CDN configuration
        ConfigVar("CDN_URL"),
        ConfigVar("CDN_AUTO_NAMING", default=True),
        StaticVar("CDN_IMAGE_EXTS", ["jpg", "jpeg", "png", "webp"]),
        StaticVar("CDN_AUDIO_EXTS", ["m4a", "mp3", "mp4"]),
        StaticVar("CDN_VIDEO_EXTS", ["mp4"]),
        ConfigVar("CDN_HOSTNAME"),
        ConfigVar("CDN_USERNAME"),
        EnvVar("CDN_PASSWORD", str),
        # Email configuration
        EnvVar("EMAIL_METHOD", str),
        EnvVar("EMAIL_TIMEOUT", int, default=10),
        ConfigVar("EMAIL_MAX_BULK_COUNT", default=100),
        EnvVar("EMAIL_FROM", str),
        EnvVar("EMAIL_TO", str),
        EnvVar("EMAIL_ADMIN", str),
        # Endpoint mapping
        ConfigVar("ENDPOINT_ERROR"),
        ConfigVar("ENDPOINT_HOME"),
        ConfigVar("ENDPOINT_LOGIN"),
        ConfigVar("ENDPOINT_PASSWORD"),
        # External services
        EnvVar("DATABASE_URL", str),
        EnvVar("GOOGLE_KEY", str),
        EnvVar("GOOGLE_CLIENT_ID", str),
        EnvVar("GOOGLE_PLACE_ID", str),
        ConfigVar("INTIME", default=False),
        EnvVar("LOCALHOST", str),
        EnvVar("MOLLIE_KEY", str),
        # SMTP configuration
        EnvVar("SMTP_HOST", str),
        EnvVar("SMTP_USERNAME", str),
        EnvVar("SMTP_PASSWORD", str),
        EnvVar("SMTP_PORT", int),
        # Social links
        ConfigVar("SOCIAL_DISCORD"),
        ConfigVar("SOCIAL_FACEBOOK"),
        ConfigVar("SOCIAL_INSTAGRAM"),
        ConfigVar("SOCIAL_PINTEREST"),
        ConfigVar("SOCIAL_TWITTER"),
        ConfigVar("SOCIAL_YOUTUBE"),
        # Website details
        ConfigVar("WEBSITE_NAME"),
        ConfigVar("WEBSITE_COUNTRY_CODE"),
        ConfigVar("WEBSITE_LANGUAGE_CODE"),
        ConfigVar("WEBSITE_FAVICON_URL"),
        ConfigVar("WEBSITE_LOGO_URL"),
        ConfigVar("WEBSITE_HEX_COLOR"),
    ]

    def __init__(self) -> None:
        load_dotenv(override=True)

    def __getattr__(self, key: str) -> Any:
        for var in self.VARS:
            if var.key == key:
                return var.value
        raise AttributeError

    def __setattr__(self, key: str, value: Any) -> None:
        for var in self.VARS:
            if var.key == key:
                var.value = value
                return
        raise AttributeError


config = Config()
