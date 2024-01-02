import json
import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

load_dotenv(override=True)


def env_str(key: str) -> str | None:
    return os.getenv(key)


def env_int(key: str) -> int | None:
    value = os.getenv(key)
    if value is not None:
        try:
            return int(value)
        except (ValueError, TypeError):
            pass


def env_bool(key: str) -> bool:
    value = os.getenv(key)
    return value in ["true", "1"]


@lru_cache
def config_var(key: str) -> Any:
    path = env_str("CONFIG_PATH")
    if path is None or not os.path.isfile(path):
        raise EnvironmentError
    with open(path, "r") as file:
        data = json.loads(file.read())
    return data.get(key)


APP_DEBUG: bool = env_bool("APP_DEBUG")
APP_SECRET: str = env_str("APP_SECRET")

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
CDN_PASSWORD: str = env_str("CDN_PASSWORD")
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

DATABASE_URL: str = env_str("DATABASE_URL")
GOOGLE_API_KEY: str = env_str("GOOGLE_API_KEY")
GOOGLE_PLACE_ID: str = env_str("GOOGLE_PLACE_ID")
LOCALHOST: str = env_str("LOCALHOST")
MOLLIE_KEY: str = env_str("MOLLIE_KEY")
SEED_EXTERNAL: bool = env_bool("SEED_EXTERNAL")

ROBOT_DEFAULT_TAGS: str = config_var("ROBOT_DEFAULT_TAGS")
ROBOT_DISALLOW_URLS: list[str] = config_var("ROBOT_DISALLOW_URLS")

SOCIAL_DISCORD: str = config_var("SOCIAL_DISCORD")
SOCIAL_FACEBOOK: str = config_var("SOCIAL_FACEBOOK")
SOCIAL_INSTAGRAM: str = config_var("SOCIAL_INSTAGRAM")
SOCIAL_PINTEREST: str = config_var("SOCIAL_PINTEREST")
SOCIAL_TWITTER: str = config_var("SOCIAL_TWITTER")
SOCIAL_YOUTUBE: str = config_var("SOCIAL_YOUTUBE")

EMAIL_METHOD: str = config_var("EMAIL_METHOD")
EMAIL_FROM: str = env_str("EMAIL_FROM")
EMAIL_TO: str = env_str("EMAIL_TO")
SMTP_HOST: str = env_str("SMTP_HOST")
SMTP_PORT: int = env_int("SMTP_PORT")
SMTP_USERNAME: str = env_str("SMTP_USERNAME")
SMTP_PASSWORD: str = env_str("SMTP_PASSWORD")

WEBSITE_NAME: str = config_var("WEBSITE_NAME")
WEBSITE_LOCALE: str = config_var("WEBSITE_LOCALE")
WEBSITE_LANGUAGE_CODE: str = config_var("WEBSITE_LANGUAGE_CODE")
WEBSITE_COUNTRY_CODE: str = config_var("WEBSITE_COUNTRY_CODE")
WEBSITE_FAVICON_URL: str = config_var("WEBSITE_FAVICON_URL")
WEBSITE_LOGO_URL: str = config_var("WEBSITE_LOGO_URL")
WEBSITE_HEX_COLOR: str = config_var("WEBSITE_HEX_COLOR")
