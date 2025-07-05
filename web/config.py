import importlib
import os
from decimal import Decimal
from typing import Any, Literal, Protocol

from dotenv import load_dotenv

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
UrlScheme = Literal["http", "https"]


class ConfigProtocol(Protocol):
    APP_ROOT: str
    APP_LOG_LEVEL: LogLevel
    APP_DEBUG: bool
    APP_DEBUG_PORT: int
    APP_URL_SCHEME: UrlScheme
    APP_OPTIMIZE: bool
    APP_SYNC_EXTERNAL: bool
    APP_SYNC_STATIC: bool
    APP_SYNC_TIMEOUT_S: int
    WORKER_ENABLED: bool
    WORKER_INTERVAL_S: int

    AUTH_JWT_COOKIE_NAME: str
    AUTH_JWT_ENCODE_ALGORITHM: str
    AUTH_JWT_DECODE_ALGORITHMS: list[str]
    AUTH_JWT_SECRET: str
    AUTH_JWT_ALLOW_GUEST: bool
    AUTH_JWT_EXPIRES_S: int
    AUTH_JWT_DECODE_LEEWAY_S: int
    AUTH_KEY_HEADER_NAME: str
    AUTH_CSRF_COOKIE_NAME: str
    AUTH_CSRF_METHODS: list[str]

    ENDPOINT_HOME: str
    ENDPOINT_ERROR: str
    ENDPOINT_LOGIN: str
    ENDPOINT_PASSWORD_RECOVERY: str

    DATABASE_URL: str
    LOCALHOST_URL: str
    MOLLIE_KEY: str
    GOOGLE_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_PLACE_ID: str
    INTIME_INTEGRATION: bool

    CDN_URL: str
    CDN_HOSTNAME: str
    CDN_USERNAME: str
    CDN_PASSWORD: str
    CDN_AUTO_NAMING: bool
    CDN_IMAGE_EXTS: list[str]
    CDN_AUDIO_EXTS: list[str]
    CDN_VIDEO_EXTS: list[str]

    EMAIL_METHOD: str
    EMAIL_TIMEOUT_S: int
    EMAIL_MAX_RECIPIENTS: int
    EMAIL_FROM: str
    EMAIL_TO: str
    EMAIL_ADMIN: str
    SMTP_HOSTNAME: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    WEBSITE_NAME: str
    WEBSITE_COUNTRY_CODE: str
    WEBSITE_LANGUAGE_CODE: str
    WEBSITE_FAVICON_URL: str
    WEBSITE_LOGO_URL: str
    WEBSITE_HEX_COLOR: str

    BUSINESS_NAME: str
    BUSINESS_EMAIL: str
    BUSINESS_CC: str
    BUSINESS_VAT: str
    BUSINESS_VAT_RATE: Decimal
    BUSINESS_VAT_REVERSE_CHARGE: bool
    BUSINESS_STREET: str
    BUSINESS_CITY: str
    BUSINESS_ZIP_CODE: str
    BUSINESS_COUNTRY: str
    BUSINESS_COUNTRY_CODE: str

    SOCIAL_DISCORD: str
    SOCIAL_FACEBOOK: str
    SOCIAL_INSTAGRAM: str
    SOCIAL_PINTEREST: str
    SOCIAL_TWITTER: str
    SOCIAL_YOUTUBE: str


class Config:
    _config: ConfigProtocol | None = None

    def __init__(self) -> None:
        load_dotenv(override=True)

    def __getattr__(self, name: str) -> Any:
        if self._config is None:
            self._setup()
        return getattr(self._config, name)

    def _setup(self) -> None:
        module_path = os.environ["APP_CONFIG_MODULE"]
        config = importlib.import_module(module_path)
        self._validate(config)
        self._config = config

    def _validate(self, config: ConfigProtocol) -> None:
        pass


def env_var(key: str, type_: Any, default: Any = None) -> Any:
    value = os.getenv(key, default)
    if type_ is str:
        return value
    if type_ is int:
        return int(value)
    if type_ is bool:
        return value in ["true", "1"]


config: ConfigProtocol = Config()
