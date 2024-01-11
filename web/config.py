import json
import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

load_dotenv(override=True)


@lru_cache
def env_var(key: str, type_: str | int | bool) -> str | int | bool:
    value = os.getenv(key)
    if isinstance(type_, int):
        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
    elif isinstance(type_, bool):
        value = value in ["true", "1"]
    return value


@lru_cache
def config_var(key: str) -> Any:
    path = env_var("CONFIG_PATH", str)
    if path is None or not os.path.isfile(path):
        raise EnvironmentError
    with open(path, "r") as file:
        data = json.loads(file.read())
    return data.get(key)


APP_DEBUG: bool = env_var("APP_DEBUG", bool)
APP_SECRET: str = env_var("APP_SECRET", str)

BUSINESS_CC: str = config_var("BUSINESS_CC")
BUSINESS_CITY: str = config_var("BUSINESS_CITY")
BUSINESS_COUNTRY_CODE: str = config_var("BUSINESS_COUNTRY_CODE")
BUSINESS_COUNTRY: str = config_var("BUSINESS_COUNTRY")
BUSINESS_EMAIL: str = config_var("BUSINESS_EMAIL")
BUSINESS_NAME: str = config_var("BUSINESS_NAME")
BUSINESS_STREET: str = config_var("BUSINESS_STREET")
BUSINESS_VAT_RATE: float = config_var("BUSINESS_VAT_RATE")
BUSINESS_VAT_REVERSE_CHARGE: bool = config_var("BUSINESS_VAT_REVERSE_CHARGE")
BUSINESS_VAT: str = config_var("BUSINESS_VAT")
BUSINESS_ZIP_CODE: str = config_var("BUSINESS_ZIP_CODE")

CDN_AUTO_NAMING: bool = config_var("CDN_AUTO_NAMING")
CDN_HOSTNAME: str = config_var("CDN_HOSTNAME")
CDN_USERNAME: str = config_var("CDN_USERNAME")
CDN_PASSWORD: str = env_var("CDN_PASSWORD", str)
CDN_ZONE: str = config_var("CDN_ZONE")
CDN_URL: str = config_var("CDN_URL")
CDN_IMAGE_EXTS: list[str] = ["jpg", "jpeg", "png", "webp"]
CDN_VIDEO_EXTS: list[str] = ["mp4"]

ENDPOINT_ERROR: str = config_var("ENDPOINT_ERROR")
ENDPOINT_HOME: str = config_var("ENDPOINT_HOME")
ENDPOINT_LOGIN: str = config_var("ENDPOINT_LOGIN")
ENDPOINT_MOLLIE: str = config_var("ENDPOINT_MOLLIE")
ENDPOINT_USER: str = config_var("ENDPOINT_USER")
ENDPOINT_PASSWORD: str = config_var("ENDPOINT_PASSWORD")
ENDPOINT_ORDER: str = config_var("ENDPOINT_ORDER")

DATABASE_URL: str = env_var("DATABASE_URL", str)
GOOGLE_KEY: str = env_var("GOOGLE_KEY", str)
GOOGLE_PLACE_ID: str = env_var("GOOGLE_PLACE_ID", str)
LOCALHOST: str = env_var("LOCALHOST", str)
MOLLIE_KEY: str = env_var("MOLLIE_KEY", str)
SEED_EXTERNAL: bool = env_var("SEED_EXTERNAL", bool)

ROBOT_DEFAULT_TAGS: str = config_var("ROBOT_DEFAULT_TAGS")
ROBOT_DISALLOW_URLS: list[str] = config_var("ROBOT_DISALLOW_URLS")

SOCIAL_DISCORD: str = config_var("SOCIAL_DISCORD")
SOCIAL_FACEBOOK: str = config_var("SOCIAL_FACEBOOK")
SOCIAL_INSTAGRAM: str = config_var("SOCIAL_INSTAGRAM")
SOCIAL_PINTEREST: str = config_var("SOCIAL_PINTEREST")
SOCIAL_TWITTER: str = config_var("SOCIAL_TWITTER")
SOCIAL_YOUTUBE: str = config_var("SOCIAL_YOUTUBE")

EMAIL_METHOD: str = config_var("EMAIL_METHOD")
EMAIL_FROM: str = env_var("EMAIL_FROM", str)
EMAIL_TO: str = env_var("EMAIL_TO", str)
SMTP_HOST: str = env_var("SMTP_HOST", str)
SMTP_PORT: int = env_var("SMTP_PORT", int)
SMTP_USERNAME: str = env_var("SMTP_USERNAME", str)
SMTP_PASSWORD: str = env_var("SMTP_PASSWORD", str)

WEBSITE_URL: str = env_var("WEBSITE_URL", str)
WEBSITE_NAME: str = config_var("WEBSITE_NAME")
WEBSITE_LOCALE: str = config_var("WEBSITE_LOCALE")
WEBSITE_LANGUAGE_CODE: str = config_var("WEBSITE_LANGUAGE_CODE")
WEBSITE_COUNTRY_CODE: str = config_var("WEBSITE_COUNTRY_CODE")
WEBSITE_FAVICON_URL: str = config_var("WEBSITE_FAVICON_URL")
WEBSITE_LOGO_URL: str = config_var("WEBSITE_LOGO_URL")
WEBSITE_HEX_COLOR: str = config_var("WEBSITE_HEX_COLOR")
