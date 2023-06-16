import json
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@lru_cache
def env_var(
    key: str,
    as_int: bool = False,
    as_boolean: bool = False,
    optional: bool = False,
) -> str:
    """Get an environment variable."""
    # Get value from environment
    value = os.getenv(key)
    # Check if key is set
    if (value is None or value == "") and not optional:
        raise KeyError(f"Environment variable {key} is not set")
    # Parse value
    if as_int:
        try:
            return int(value)
        except ValueError:
            if not optional:
                raise ValueError(f"Environment variable {key} is not an integer")
    if as_boolean:
        return value in ["true", "1"]
    # Set value
    return value


@lru_cache
def config_var(
    key: str,
    optional: bool = False,
) -> any:
    """Get a config variable."""
    # Get config path
    path = env_var("CONFIG_PATH")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file {path} does not exist")
    # Get value from config file
    with open(path, "r") as file:
        data = json.loads(file.read())
    value = data.get(key)
    # Check if key is set
    if value is None and not optional:
        raise KeyError(f"Config variable {key} is not set")
    # Set value
    return value


APP_DEBUG: bool = env_var("APP_DEBUG", as_boolean=True)
APP_SECRET: str = env_var("APP_SECRET")

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
CDN_HOSTNAME: str = env_var("CDN_HOSTNAME")
CDN_IMAGE_EXTS: list[str] = ["jpg", "jpeg", "png", "webp"]
CDN_PASSWORD: str = env_var("CDN_PASSWORD")
CDN_URL: str = env_var("CDN_URL")
CDN_USERNAME: str = env_var("CDN_USERNAME")
CDN_VIDEO_EXTS: list[str] = ["mp4"]
CDN_ZONE: str = env_var("CDN_ZONE")

ENDPOINT_ERROR: str | None = config_var("ENDPOINT_ERROR", optional=True)
ENDPOINT_HOME: str | None = config_var("ENDPOINT_HOME", optional=True)
ENDPOINT_LOGIN: str | None = config_var("ENDPOINT_LOGIN", optional=True)
ENDPOINT_USER: str | None = config_var("ENDPOINT_USER", optional=True)

DATABASE_URL: str = env_var("DATABASE_URL")
GOOGLE_API_KEY: str = env_var("GOOGLE_API_KEY", optional=True)
GOOGLE_PLACE_ID: str = env_var("GOOGLE_PLACE_ID", optional=True)
LOCALHOST: str = env_var("LOCALHOST", optional=True)
MOLLIE_KEY: str = env_var("MOLLIE_KEY", optional=True)
SEED_EXTERNAL: bool = env_var("SEED_EXTERNAL", as_boolean=True)

ROBOT_DEFAULT_TAGS: str = config_var("ROBOT_DEFAULT_TAGS")
ROBOT_DISALLOW_URLS: list[str] = config_var("ROBOT_DISALLOW_URLS")

SOCIAL_DISCORD: str | None = config_var("SOCIAL_DISCORD", optional=True)
SOCIAL_FACEBOOK: str | None = config_var("SOCIAL_FACEBOOK", optional=True)
SOCIAL_INSTAGRAM: str | None = config_var("SOCIAL_INSTAGRAM", optional=True)
SOCIAL_PINTEREST: str | None = config_var("SOCIAL_PINTEREST", optional=True)
SOCIAL_TWITTER: str | None = config_var("SOCIAL_TWITTER", optional=True)
SOCIAL_YOUTUBE: str | None = config_var("SOCIAL_YOUTUBE", optional=True)

EMAIL_OVERRIDE: str = env_var("EMAIL_OVERRIDE", optional=True)
SENDGRID_KEY: str = env_var("SENDGRID_KEY", optional=True)
SMTP_HOST: str = env_var("SMTP_HOST", optional=True)
SMTP_PASSWORD: str = env_var("SMTP_PASSWORD", optional=True)
SMTP_PORT: int = env_var("SMTP_PORT", as_int=True, optional=True)
SMTP_USERNAME: str = env_var("SMTP_USERNAME", optional=True)

WEBSITE_COUNTRY_CODE: str = config_var("WEBSITE_COUNTRY_CODE")
WEBSITE_FAVICON_URL: str = config_var("WEBSITE_FAVICON_URL")
WEBSITE_HEX_COLOR: str = config_var("WEBSITE_HEX_COLOR")
WEBSITE_LANGUAGE_CODE: str = config_var("WEBSITE_LANGUAGE_CODE")
WEBSITE_LOCALE: str = config_var("WEBSITE_LOCALE")
WEBSITE_LOGO_URL: str = config_var("WEBSITE_LOGO_URL")
WEBSITE_NAME: str = config_var("WEBSITE_NAME")
