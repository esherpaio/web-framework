import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def load_config(path: str) -> None:
    with open(path, "r") as file:
        data = json.loads(file.read())
    for k, v in data.items():
        if hasattr(sys.modules[__name__], k):
            setattr(sys.modules[__name__], k, v)


BUSINESS_CC = ""
BUSINESS_CITY = ""
BUSINESS_COUNTRY = ""
BUSINESS_COUNTRY_CODE = ""
BUSINESS_EMAIL = ""
BUSINESS_LANGUAGE_CODE = ""
BUSINESS_LOCALE = ""
BUSINESS_NAME = ""
BUSINESS_STREET = ""
BUSINESS_VAT = ""
BUSINESS_VAT_RATE = 1.00
BUSINESS_VAT_REVERSE_CHARGE = False
BUSINESS_ZIP_CODE = ""

WEBSITE_FAVICON = ""
WEBSITE_HEX_COLOR = ""
WEBSITE_LANGUAGE = ""
WEBSITE_NAME = ""
WEBSITE_URL = ""

SOCIAL_DISCORD = ""
SOCIAL_FACEBOOK = ""
SOCIAL_INSTAGRAM = ""
SOCIAL_TWITTER = ""
SOCIAL_YOUTUBE = ""

DATABASE_URL = os.getenv("DATABASE_URL")
DIR = os.path.dirname(os.path.realpath(__file__))
LOCALHOST = os.getenv("LOCALHOST")
MOLLIE_KEY = os.getenv("MOLLIE_KEY")
MOLLIE_TEST = MOLLIE_KEY.startswith("test")
SEED_EXTERNAL = os.getenv("SEED_EXTERNAL") in ["true", "1"]
SENDGRID_KEY = os.getenv("SENDGRID_KEY")

CDN_HOSTNAME = os.getenv("CDN_HOSTNAME")
CDN_PASSWORD = os.getenv("CDN_PASSWORD")
CDN_URL = os.getenv("CDN_URL")
CDN_USERNAME = os.getenv("CDN_USERNAME")
CDN_ZONE = os.getenv("CDN_ZONE")

EXTENSIONS_IMAGE = ["jpg", "jpeg", "png", "webp"]
EXTENSIONS_VIDEO = ["mp4"]

EMAIL_LOGO = ""
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_UNSUBSCRIBE = ""

APP_DEBUG = os.getenv("APP_DEBUG") in ["true", "1"]
APP_SECRET = os.getenv("APP_SECRET")

ENDPOINT_ERROR = ""
ENDPOINT_HOME = ""
ENDPOINT_LOGIN = ""

ROBOT_DEFAULT_TAGS = "index,follow"
ROBOT_DISALLOW_URLS = []
