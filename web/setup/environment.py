import importlib
import os
from decimal import Decimal
from typing import Any, Literal, Protocol

from dotenv import load_dotenv

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
UrlScheme = Literal["http", "https"]
MailMethod = Literal["SMTP"]
CsrfMethods = Literal["POST", "PUT", "PATCH", "DELETE"]


class _Protocol(Protocol):
    BASE_DIR: str
    DEBUG: bool
    DEBUG_PORT: int
    LOG_LEVEL: LogLevel
    URL_SCHEME: UrlScheme

    WORKER_ENABLED: bool
    WORKER_INTERVAL_S: int

    DATABASE_URL: str
    LOCALHOST_URL: str | None

    ENDPOINT_HOME: str
    ENDPOINT_ERROR: str
    ENDPOINT_LOGIN: str
    ENDPOINT_PASSWORD_RECOVERY: str

    LOCALE_LANGUAGE_CODE: str
    LOCALE_COUNTRY_CODE: str

    AUTOMATE_EXTERNAL: bool
    AUTOMATE_STATIC: bool
    AUTOMATE_TIMEOUT_S: int
    OPTIMIZER_ENABLED: bool

    AUTH_JWT_SECRET: str
    AUTH_JWT_ALLOW_GUEST: bool
    AUTH_JWT_EXPIRES_S: int
    AUTH_JWT_COOKIE: str
    AUTH_JWT_ENCODE_ALGORITHM: str
    AUTH_JWT_DECODE_ALGORITHMS: list[str]
    AUTH_JWT_DECODE_LEEWAY_S: int

    AUTH_CSRF_COOKIE: str
    AUTH_CSRF_METHODS: CsrfMethods

    AUTH_KEY_HEADER: str

    MAIL_METHOD: MailMethod
    MAIL_TIMEOUT_S: int
    MAIL_MAX_RECEIVERS: int
    MAIL_SENDER: str
    MAIL_RECEIVER: str
    MAIL_ADMIN: str

    MAIL_LOG_ENABLED: bool
    MAIL_LOG_LEVEL: LogLevel
    MAIL_LOG_PREFIX: str

    SMTP_HOSTNAME: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    CDN_BASE_URL: str
    CDN_AUTO_NAMING: bool
    CDN_IMAGE_EXTS: list[str]
    CDN_AUDIO_EXTS: list[str]
    CDN_VIDEO_EXTS: list[str]

    FTP_HOSTNAME: str
    FTP_USERNAME: str
    FTP_PASSWORD: str

    GOOGLE_API_KEY: str | None
    GOOGLE_CLIENT_ID: str | None
    GOOGLE_PLACE_ID: str | None

    MOLLIE_API_KEY: str | None

    INTIME_ENABLED: bool

    META_BRAND_NAME: str | None
    META_WEBSITE_NAME: str
    META_LOGO_URL: str
    META_FAVICON_URL: str
    META_COLOR_HEX: str

    SOCIAL_DISCORD: str | None
    SOCIAL_FACEBOOK: str | None
    SOCIAL_INSTAGRAM: str | None
    SOCIAL_PINTEREST: str | None
    SOCIAL_TWITTER: str | None
    SOCIAL_YOUTUBE: str | None

    BUSINESS_NAME: str
    BUSINESS_EMAIL: str
    BUSINESS_LOGO_URL: str
    BUSINESS_REGISTRATION_NUMBER: str
    BUSINESS_VAT_NUMBER: str
    BUSINESS_VAT_REVERSE_RATE: Decimal
    BUSINESS_STREET: str
    BUSINESS_CITY: str
    BUSINESS_ZIP_CODE: str
    BUSINESS_COUNTRY: str
    BUSINESS_COUNTRY_CODE: str


class Config:
    _config: _Protocol | None = None

    def __init__(self) -> None:
        load_dotenv(override=True)

    def __getattr__(self, name: str) -> Any:
        if self._config is None:
            self._setup()
        return getattr(self._config, name)

    def _setup(self) -> None:
        module_path = os.getenv("SUMMIT_CONFIG_MODULE", "config")
        print(module_path)
        config_ = importlib.import_module(module_path)
        self._validate(config_)
        self._config = config_

    def _validate(self, config_: _Protocol) -> None:
        pass


def env_var(key: str, type_: type[str | int | bool], default: Any = None) -> Any:
    value = os.getenv(key, default)
    if type_ is str:
        return value
    if type_ is int:
        return int(value)
    if type_ is bool:
        return value in ["true", "1"]


config: _Protocol = Config()
