import json
import os
import sys
from typing import Union

from dotenv import load_dotenv

load_dotenv()


# Type to indicate a config attribute,
# that needs to be set from a JSON file
class _ToSet:
    def __bool__(self) -> bool:
        return False


# Type annotations for _ToSet
_Str = Union[str, None, _ToSet]
_Int = Union[int, None, _ToSet]
_Float = Union[float, None, _ToSet]
_Bool = Union[bool, None, _ToSet]
_ListStr = Union[list[str], _ToSet]


def load_config(path: str) -> None:
    """Load and check the config."""

    # Read config JSON
    with open(path, "r") as file:
        data = json.loads(file.read())

    # Count config attributes
    config_len = 0
    for x in dir(sys.modules[__name__]):
        attr = getattr(sys.modules[__name__], x)
        if isinstance(attr, _ToSet):
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


APP_DEBUG: bool = os.getenv("APP_DEBUG") in ["true", "1"]
APP_SECRET: str = os.getenv("APP_SECRET")

BUSINESS_CC: _Str = _ToSet()
BUSINESS_CITY: _Str = _ToSet()
BUSINESS_COUNTRY: _Str = _ToSet()
BUSINESS_COUNTRY_CODE: _Str = _ToSet()
BUSINESS_EMAIL: _Str = _ToSet()
BUSINESS_NAME: _Str = _ToSet()
BUSINESS_STREET: _Str = _ToSet()
BUSINESS_VAT: _Str = _ToSet()
BUSINESS_VAT_RATE: _Float = _ToSet()
BUSINESS_VAT_REVERSE_CHARGE: _Bool = _ToSet()
BUSINESS_ZIP_CODE: _Str = _ToSet()

CDN_AUTO_NAMING: _Bool = _ToSet()
CDN_HOSTNAME: str = os.getenv("CDN_HOSTNAME")
CDN_IMAGE_EXTS: list[str] = ["jpg", "jpeg", "png", "webp"]
CDN_PASSWORD: str = os.getenv("CDN_PASSWORD")
CDN_URL: str = os.getenv("CDN_URL")
CDN_USERNAME: str = os.getenv("CDN_USERNAME")
CDN_VIDEO_EXTS: list[str] = ["mp4"]
CDN_ZONE: str = os.getenv("CDN_ZONE")

DATABASE_URL: str = os.getenv("DATABASE_URL")

EMAIL_FROM: str = os.getenv("EMAIL_FROM")
EMAIL_LOGO_URL: _Str = _ToSet()
EMAIL_TO: str = os.getenv("EMAIL_TO")
EMAIL_UNSUBSCRIBE_URL: _Str = _ToSet()

ENDPOINT_ERROR: _Str = _ToSet()
ENDPOINT_HOME: _Str = _ToSet()
ENDPOINT_LOGIN: _Str = _ToSet()
ENDPOINT_USER: _Str = _ToSet()

LOCALHOST: str = os.getenv("LOCALHOST")

MOLLIE_KEY: str = os.getenv("MOLLIE_KEY")

ROBOT_DEFAULT_TAGS: _Str = _ToSet()
ROBOT_DISALLOW_URLS: _ListStr = _ToSet()

SEED_EXTERNAL: bool = os.getenv("SEED_EXTERNAL") in ["true", "1"]

SENDGRID_KEY: str = os.getenv("SENDGRID_KEY")

SOCIAL_DISCORD: _Str = _ToSet()
SOCIAL_FACEBOOK: _Str = _ToSet()
SOCIAL_INSTAGRAM: _Str = _ToSet()
SOCIAL_PINTEREST: _Str = _ToSet()
SOCIAL_TWITTER: _Str = _ToSet()
SOCIAL_YOUTUBE: _Str = _ToSet()

WEBSITE_COUNTRY_CODE: _Str = _ToSet()
WEBSITE_FAVICON_URL: _Str = _ToSet()
WEBSITE_HEX_COLOR: _Str = _ToSet()
WEBSITE_LANGUAGE_CODE: _Str = _ToSet()
WEBSITE_LOCALE: _Str = _ToSet()
WEBSITE_NAME: _Str = _ToSet()
