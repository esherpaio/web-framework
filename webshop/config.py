import json
import os
import sys
from typing import Type

from dotenv import load_dotenv

load_dotenv()


# Type to indicate a config attribute,
# that needs to be set from a JSON file
class _ToSet:
    pass


# Type annotations for _ToSet
Str = str | Type[_ToSet]
Int = int | Type[_ToSet]
Float = float | Type[_ToSet]
Bool = bool | Type[_ToSet]
ListStr = list[str] | Type[_ToSet]


def load_config(path: str) -> None:
    """Load and check the config."""

    # Read config JSON
    with open(path, "r") as file:
        data = json.loads(file.read())

    # Count config attributes
    config_len = 0
    for x in dir(sys.modules[__name__]):
        attr = getattr(sys.modules[__name__], x)
        if attr == _ToSet:
            config_len += 1

    # Check if all attributes are set
    if config_len != len(data.keys()):
        raise KeyError("Not all config attributes are set")

    # Check if all config keys exist
    for k, v in data.items():
        if hasattr(sys.modules[__name__], k):
            setattr(sys.modules[__name__], k, v)
        else:
            raise KeyError(f"Config key {k} does not exist")


BUSINESS_CC: Str = _ToSet
BUSINESS_CITY: Str = _ToSet
BUSINESS_COUNTRY: Str = _ToSet
BUSINESS_COUNTRY_CODE: Str = _ToSet
BUSINESS_EMAIL: Str = _ToSet
BUSINESS_NAME: Str = _ToSet
BUSINESS_STREET: Str = _ToSet
BUSINESS_VAT: Str = _ToSet
BUSINESS_VAT_RATE: Float = _ToSet
BUSINESS_VAT_REVERSE_CHARGE: Bool = _ToSet
BUSINESS_ZIP_CODE: Str = _ToSet

WEBSITE_COUNTRY_CODE: Str = _ToSet
WEBSITE_FAVICON_URL: Str = _ToSet
WEBSITE_HEX_COLOR: Str = _ToSet
WEBSITE_LANGUAGE_CODE: Str = _ToSet
WEBSITE_LOCALE: Str = _ToSet
WEBSITE_NAME: Str = _ToSet

ENDPOINT_ERROR: Str = _ToSet
ENDPOINT_HOME: Str = _ToSet
ENDPOINT_LOGIN: Str = _ToSet
ENDPOINT_USER: Str = _ToSet

ROBOT_DEFAULT_TAGS: Str = _ToSet
ROBOT_DISALLOW_URLS: ListStr = _ToSet

SOCIAL_DISCORD: Str = _ToSet
SOCIAL_FACEBOOK: Str = _ToSet
SOCIAL_INSTAGRAM: Str = _ToSet
SOCIAL_TWITTER: Str = _ToSet
SOCIAL_YOUTUBE: Str = _ToSet

APP_DEBUG: bool = os.getenv("APP_DEBUG") in ["true", "1"]
APP_SECRET: str = os.getenv("APP_SECRET")

CDN_HOSTNAME: str = os.getenv("CDN_HOSTNAME")
CDN_IMAGE_EXTS: list[str] = ["jpg", "jpeg", "png", "webp"]
CDN_PASSWORD: str = os.getenv("CDN_PASSWORD")
CDN_URL: str = os.getenv("CDN_URL")
CDN_USERNAME: str = os.getenv("CDN_USERNAME")
CDN_VIDEO_EXTS: list[str] = ["mp4"]
CDN_ZONE: str = os.getenv("CDN_ZONE")

EMAIL_FROM: str = os.getenv("EMAIL_FROM")
EMAIL_LOGO_URL: Str = _ToSet
EMAIL_UNSUBSCRIBE_URL: Str = _ToSet

DATABASE_URL: str = os.getenv("DATABASE_URL")
LOCALHOST: str = os.getenv("LOCALHOST")
MOLLIE_KEY: str = os.getenv("MOLLIE_KEY")
MOLLIE_TEST: bool = MOLLIE_KEY.startswith("test")
SEED_EXTERNAL: bool = os.getenv("SEED_EXTERNAL") in ["true", "1"]
SENDGRID_KEY: str = os.getenv("SENDGRID_KEY")
