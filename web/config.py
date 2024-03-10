import json
import os
from functools import cached_property
from typing import Any

from dotenv import load_dotenv

from web.libs.utils import Singleton

#
# Types
#


class StaticVar:
    def __init__(self, value: Any) -> None:
        self.value = value


class EnvVar:
    def __init__(self, key: str, type_: Any, default: Any = None) -> None:
        self.key = key
        self.type = type_
        self.default = default

    @cached_property
    def value(self) -> Any:
        return self.parse(os.getenv(self.key, self.default))

    def parse(self, value: str, type_: Any = None) -> Any:
        if type_ is None:
            type_ = self.type
        if type_ == str:
            return value
        if type_ == int:
            try:
                return int(value)
            except (ValueError, TypeError):
                pass
        if type_ == bool:
            return value in ["true", "1"]
        if type_ == list:
            return [self.parse(x, self.type) for x in value.split(",")]


class ConfigVar:
    def __init__(self, key: str) -> None:
        self.key = key

    @cached_property
    def value(self) -> Any:
        path = EnvVar("APP_CONFIG", str).value
        if path is None or not os.path.isfile(path):
            raise EnvironmentError
        with open(path, "r") as file_:
            data = json.loads(file_.read())
        return data.get(self.key)


#
# Classes
#


class Config(metaclass=Singleton):
    VARS: dict[str, StaticVar | EnvVar | ConfigVar] = {
        "APP_CACHE": EnvVar("APP_CACHE", bool, True),
        "APP_DEBUG": EnvVar("APP_DEBUG", bool, False),
        "APP_SECRET": EnvVar("APP_SECRET", str),
        "APP_SYNC_EXT": EnvVar("APP_SYNC_EXT", bool),
        "APP_STATIC": EnvVar("APP_STATIC", bool, True),
        "BUSINESS_CC": ConfigVar("BUSINESS_CC"),
        "BUSINESS_CITY": ConfigVar("BUSINESS_CITY"),
        "BUSINESS_COUNTRY_CODE": ConfigVar("BUSINESS_COUNTRY_CODE"),
        "BUSINESS_COUNTRY": ConfigVar("BUSINESS_COUNTRY"),
        "BUSINESS_EMAIL": ConfigVar("BUSINESS_EMAIL"),
        "BUSINESS_NAME": ConfigVar("BUSINESS_NAME"),
        "BUSINESS_STREET": ConfigVar("BUSINESS_STREET"),
        "BUSINESS_VAT_RATE": ConfigVar("BUSINESS_VAT_RATE"),
        "BUSINESS_VAT_REVERSE_CHARGE": ConfigVar("BUSINESS_VAT_REVERSE_CHARGE"),
        "BUSINESS_VAT": ConfigVar("BUSINESS_VAT"),
        "BUSINESS_ZIP_CODE": ConfigVar("BUSINESS_ZIP_CODE"),
        "CDN_AUTO_NAMING": ConfigVar("CDN_AUTO_NAMING"),
        "CDN_HOSTNAME": ConfigVar("CDN_HOSTNAME"),
        "CDN_USERNAME": ConfigVar("CDN_USERNAME"),
        "CDN_PASSWORD": EnvVar("CDN_PASSWORD", str),
        "CDN_ZONE": ConfigVar("CDN_ZONE"),
        "CDN_URL": ConfigVar("CDN_URL"),
        "CDN_IMAGE_EXTS": StaticVar(["jpg", "jpeg", "png", "webp"]),
        "CDN_VIDEO_EXTS": StaticVar(["mp4"]),
        "EMAIL_METHOD": EnvVar("EMAIL_METHOD", str),
        "EMAIL_FROM": EnvVar("EMAIL_FROM", str),
        "EMAIL_TO": EnvVar("EMAIL_TO", str),
        "EMAIL_ADMIN": EnvVar("EMAIL_ADMIN", str),
        "ENDPOINT_ERROR": ConfigVar("ENDPOINT_ERROR"),
        "ENDPOINT_HOME": ConfigVar("ENDPOINT_HOME"),
        "ENDPOINT_LOGIN": ConfigVar("ENDPOINT_LOGIN"),
        "ENDPOINT_MOLLIE": ConfigVar("ENDPOINT_MOLLIE"),
        "ENDPOINT_USER": ConfigVar("ENDPOINT_USER"),
        "ENDPOINT_PASSWORD": ConfigVar("ENDPOINT_PASSWORD"),
        "ENDPOINT_ORDER": ConfigVar("ENDPOINT_ORDER"),
        "DATABASE_URL": EnvVar("DATABASE_URL", str),
        "GOOGLE_CLIENT_ID": EnvVar("GOOGLE_CLIENT_ID", str),
        "GOOGLE_KEY": EnvVar("GOOGLE_KEY", str),
        "GOOGLE_PLACE_ID": EnvVar("GOOGLE_PLACE_ID", str),
        "LOCALHOST": EnvVar("LOCALHOST", str),
        "INTIME": EnvVar("INTIME", bool, False),
        "MOLLIE_KEY": EnvVar("MOLLIE_KEY", str),
        "SOCIAL_DISCORD": ConfigVar("SOCIAL_DISCORD"),
        "SOCIAL_FACEBOOK": ConfigVar("SOCIAL_FACEBOOK"),
        "SOCIAL_INSTAGRAM": ConfigVar("SOCIAL_INSTAGRAM"),
        "SOCIAL_PINTEREST": ConfigVar("SOCIAL_PINTEREST"),
        "SOCIAL_TWITTER": ConfigVar("SOCIAL_TWITTER"),
        "SOCIAL_YOUTUBE": ConfigVar("SOCIAL_YOUTUBE"),
        "SMTP_HOST": EnvVar("SMTP_HOST", str),
        "SMTP_PORT": EnvVar("SMTP_PORT", int),
        "SMTP_USERNAME": EnvVar("SMTP_USERNAME", str),
        "SMTP_PASSWORD": EnvVar("SMTP_PASSWORD", str),
        "WEBSITE_URL": EnvVar("WEBSITE_URL", str),
        "WEBSITE_NAME": ConfigVar("WEBSITE_NAME"),
        "WEBSITE_LOCALE": ConfigVar("WEBSITE_LOCALE"),
        "WEBSITE_LANGUAGE_CODE": ConfigVar("WEBSITE_LANGUAGE_CODE"),
        "WEBSITE_COUNTRY_CODE": ConfigVar("WEBSITE_COUNTRY_CODE"),
        "WEBSITE_FAVICON_URL": ConfigVar("WEBSITE_FAVICON_URL"),
        "WEBSITE_LOGO_URL": ConfigVar("WEBSITE_LOGO_URL"),
        "WEBSITE_HEX_COLOR": ConfigVar("WEBSITE_HEX_COLOR"),
    }

    def __init__(self) -> None:
        load_dotenv(override=True)

    def __getattr__(self, key: str) -> Any:
        if key in self.VARS:
            return self.VARS[key].value
        raise AttributeError

    def __setattr__(self, key: str, value: Any) -> None:
        self.VARS[key] = value


config = Config()
