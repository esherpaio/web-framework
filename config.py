import os
from decimal import Decimal

from web.config import env_var

# Application
# NOTE: keep the secret key used in production secret
# NOTE: do not run with debug turned on in production

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_LOG_LEVEL = env_var("APP_LOG_LEVEL", str, default="INFO")
APP_DEBUG = env_var("APP_DEBUG", bool, default=False)
APP_DEBUG_PORT = env_var("APP_DEBUG_PORT", int, default=5000)
APP_URL_SCHEME = env_var("APP_URL_SCHEME", str, default="https")
APP_OPTIMIZE = env_var("APP_OPTIMIZE", bool, default=False)
APP_SYNC_EXTERNAL = env_var("APP_SYNC_EXTERNAL", bool, default=True)
APP_SYNC_STATIC = env_var("APP_SYNC_STATIC", bool, default=True)
APP_SYNC_TIMEOUT_S = env_var("APP_SYNC_TIMEOUT_S", int, default=10)

WORKER_ENABLED = env_var("WORKER_ENABLED", bool, default=False)
WORKER_INTERVAL_S = env_var("WORKER_INTERVAL_S", int, default=300)

# Authentication

AUTH_JWT_COOKIE_NAME = "access_token"
AUTH_JWT_ENCODE_ALGORITHM = "HS256"
AUTH_JWT_DECODE_ALGORITHMS = ["HS256"]
AUTH_JWT_SECRET = env_var("AUTH_JWT_SECRET", str)
AUTH_JWT_ALLOW_GUEST = env_var("AUTH_JWT_ALLOW_GUEST", bool, default=False)
AUTH_JWT_EXPIRES_S = env_var("AUTH_JWT_EXPIRES_S", int, default=3600)
AUTH_JWT_DECODE_LEEWAY_S = env_var("AUTH_JWT_DECODE_LEEWAY_S", int, default=60)

AUTH_KEY_HEADER_NAME = "Authorization"

AUTH_CSRF_COOKIE_NAME = "csrf_token"
AUTH_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

# Endpoints

ENDPOINT_HOME = None
ENDPOINT_ERROR = None
ENDPOINT_LOGIN = None
ENDPOINT_PASSWORD_RECOVERY = None

# Integrations

DATABASE_URL = env_var("DATABASE_URL", str)
LOCALHOST_URL = env_var("LOCALHOST_URL", str)

MOLLIE_KEY = env_var("MOLLIE_KEY", str)

GOOGLE_KEY = env_var("GOOGLE_KEY", str)
GOOGLE_CLIENT_ID = env_var("GOOGLE_CLIENT_ID", str)
GOOGLE_PLACE_ID = env_var("GOOGLE_PLACE_ID", str)

INTIME_INTEGRATION = False

# Content delivery network

CDN_URL = None
CDN_HOSTNAME = env_var("CDN_HOSTNAME", str)
CDN_USERNAME = env_var("CDN_USERNAME", str)
CDN_PASSWORD = env_var("CDN_PASSWORD", str)

CDN_AUTO_NAMING = False
CDN_IMAGE_EXTS = ["jpg", "jpeg", "png", "webp"]
CDN_AUDIO_EXTS = ["m4a", "mp3", "mp4"]
CDN_VIDEO_EXTS = ["mp4"]

# Email configuration

EMAIL_METHOD = "SMTP"
EMAIL_TIMEOUT_S = env_var("EMAIL_TIMEOUT_S", int, default=10)
EMAIL_MAX_RECIPIENTS = 100
EMAIL_FROM = env_var("EMAIL_FROM", str)
EMAIL_TO = env_var("EMAIL_TO", str)
EMAIL_ADMIN = env_var("EMAIL_ADMIN", str)

SMTP_HOSTNAME = env_var("SMTP_HOSTNAME", str)
SMTP_PORT = 587
SMTP_USERNAME = env_var("SMTP_USERNAME", str)
SMTP_PASSWORD = env_var("SMTP_PASSWORD", str)

# Website details

WEBSITE_NAME = None
WEBSITE_COUNTRY_CODE = None
WEBSITE_LANGUAGE_CODE = None
WEBSITE_FAVICON_URL = None
WEBSITE_LOGO_URL = None
WEBSITE_HEX_COLOR = None

# Business details

BUSINESS_NAME = None
BUSINESS_EMAIL = None
BUSINESS_CC = None
BUSINESS_VAT = None
BUSINESS_VAT_RATE = Decimal("1")
BUSINESS_VAT_REVERSE_CHARGE = False
BUSINESS_STREET = None
BUSINESS_CITY = None
BUSINESS_ZIP_CODE = None
BUSINESS_COUNTRY = None
BUSINESS_COUNTRY_CODE = None

# Social media links

SOCIAL_DISCORD = None
SOCIAL_FACEBOOK = None
SOCIAL_INSTAGRAM = None
SOCIAL_PINTEREST = None
SOCIAL_TWITTER = None
SOCIAL_YOUTUBE = None
