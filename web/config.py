import importlib
import os
from decimal import Decimal
from typing import Any, Protocol, cast

from web.error import ConfigError


class ConfigProtocol(Protocol):
    APP_ROOT: str
    APP_LOG_LEVEL: str
    APP_DEBUG: bool
    APP_DEBUG_PORT: int
    APP_URL_SCHEME: str
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

    ENDPOINT_HOME: str | None
    ENDPOINT_ERROR: str | None
    ENDPOINT_LOGIN: str | None
    ENDPOINT_PASSWORD_RECOVERY: str | None

    DATABASE_URL: str
    LOCALHOST_URL: str | None
    MOLLIE_KEY: str | None
    GOOGLE_KEY: str | None
    GOOGLE_CLIENT_ID: str | None
    GOOGLE_PLACE_ID: str | None
    INTIME_INTEGRATION: bool

    CDN_ENABLED: bool
    CDN_URL: str | None
    CDN_HOSTNAME: str | None
    CDN_USERNAME: str | None
    CDN_PASSWORD: str | None
    CDN_AUTO_NAMING: bool
    CDN_IMAGE_EXTS: list[str]
    CDN_AUDIO_EXTS: list[str]
    CDN_VIDEO_EXTS: list[str]

    EMAIL_METHOD: str
    EMAIL_TIMEOUT_S: int
    EMAIL_MAX_RECIPIENTS: int
    EMAIL_FROM: str | None
    EMAIL_TO: str | None
    EMAIL_ADMIN: str | None
    SMTP_HOSTNAME: str | None
    SMTP_PORT: int
    SMTP_USERNAME: str | None
    SMTP_PASSWORD: str | None

    WEBSITE_NAME: str | None
    WEBSITE_COUNTRY_CODE: str | None
    WEBSITE_LANGUAGE_CODE: str | None
    WEBSITE_FAVICON_URL: str | None
    WEBSITE_LOGO_URL: str | None
    WEBSITE_HEX_COLOR: str | None

    BUSINESS_NAME: str | None
    BUSINESS_EMAIL: str | None
    BUSINESS_CC: str | None
    BUSINESS_VAT: str | None
    BUSINESS_VAT_RATE: Decimal
    BUSINESS_VAT_REVERSE_CHARGE: bool
    BUSINESS_STREET: str | None
    BUSINESS_CITY: str | None
    BUSINESS_ZIP_CODE: str | None
    BUSINESS_COUNTRY: str | None
    BUSINESS_COUNTRY_CODE: str | None

    SOCIAL_DISCORD: str | None
    SOCIAL_FACEBOOK: str | None
    SOCIAL_INSTAGRAM: str | None
    SOCIAL_PINTEREST: str | None
    SOCIAL_TWITTER: str | None
    SOCIAL_YOUTUBE: str | None


class Config:
    _config: ConfigProtocol | None = None

    def __getattr__(self, name: str) -> Any:
        if self._config is None:
            self._setup()
        return getattr(self._config, name)

    def _setup(self) -> None:
        module_path = os.environ["APP_CONFIG_MODULE"]
        config = cast(ConfigProtocol, importlib.import_module(module_path))
        self._validate(config)
        self._config = config

    def _validate(self, config: ConfigProtocol) -> None:
        if config.CDN_ENABLED:
            if not config.CDN_URL:
                raise ConfigError("CDN_URL")
            if not config.CDN_HOSTNAME:
                raise ConfigError("CDN_HOSTNAME")
            if not config.CDN_USERNAME:
                raise ConfigError("CDN_USERNAME")
            if not config.CDN_PASSWORD:
                raise ConfigError("CDN_PASSWORD")


def get_env_var(key: str, type_: Any, default: Any = None) -> Any:
    value = os.getenv(key, default)
    if type_ is str:
        return value
    if type_ is int:
        return int(value)
    if type_ is bool:
        return value in ["true", "1"]


config: ConfigProtocol = Config()
