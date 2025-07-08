import os
from decimal import Decimal

from web.setup import env_var

#
# Application setup
# NOTE: do not run with debug turned on in production
#

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = env_var("DEBUG", bool, default=False)
DEBUG_PORT = env_var("DEBUG_PORT", int, default=5000)
LOG_LEVEL = env_var("LOG_LEVEL", str, default="INFO")
URL_SCHEME = env_var("URL_SCHEME", str, default="https")

WORKER_ENABLED = env_var("WORKER_ENABLED", bool, default=False)
WORKER_INTERVAL_S = 300

DATABASE_URL = env_var("DATABASE_URL", str)
LOCALHOST_URL = env_var("LOCALHOST_URL", str)

ENDPOINT_HOME = None
ENDPOINT_ERROR = None
ENDPOINT_LOGIN = None
ENDPOINT_PASSWORD_RECOVERY = None

LOCALE_LANGUAGE_CODE = None
LOCALE_COUNTRY_CODE = None

AUTOMATE_EXTERNAL = env_var("AUTOMATE_EXTERNAL", bool, default=False)
AUTOMATE_STATIC = env_var("AUTOMATE_STATIC", bool, default=False)
AUTOMATE_TIMEOUT_S = 10
OPTIMIZER_ENABLED = env_var("OPTIMIZER_ENABLED", bool, default=False)

#
# Authentication
# NOTE: keep the secret key used in production secret
#

AUTH_JWT_SECRET = env_var("AUTH_JWT_SECRET", str)
AUTH_JWT_ALLOW_GUEST = False
AUTH_JWT_EXPIRES_S = 3600
AUTH_JWT_COOKIE = "access_token"
AUTH_JWT_ENCODE_ALGORITHM = "HS256"
AUTH_JWT_DECODE_ALGORITHMS = ["HS256"]
AUTH_JWT_DECODE_LEEWAY_S = 60

AUTH_CSRF_COOKIE = "csrf_token"
AUTH_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

AUTH_KEY_HEADER = "Authorization"

#
# Email configuration
#

MAIL_METHOD = "SMTP"
MAIL_TIMEOUT_S = 10
MAIL_MAX_RECEIVERS = 100
MAIL_SENDER = env_var("MAIL_SENDER", str)
MAIL_RECEIVER = env_var("MAIL_RECEIVER", str)
MAIL_ADMIN = None

MAIL_LOG_ENABLED = env_var("MAIL_LOG_ENABLED", bool, default=False)
MAIL_LOG_LEVEL = "ERROR"
MAIL_LOG_PREFIX = "Summit"

SMTP_HOSTNAME = env_var("SMTP_HOSTNAME", str)
SMTP_PORT = env_var("SMTP_PORT", int)
SMTP_USERNAME = env_var("SMTP_USERNAME", str)
SMTP_PASSWORD = env_var("SMTP_PASSWORD", str)

#
# Content delivery network
#

CDN_BASE_URL = env_var("CDN_BASE_URL", str)
CDN_AUTO_NAMING = False
CDN_IMAGE_EXTS = ["jpg", "jpeg", "png", "webp"]
CDN_AUDIO_EXTS = ["m4a", "mp3", "mp4"]
CDN_VIDEO_EXTS = ["mp4"]

FTP_HOSTNAME = env_var("FTP_HOSTNAME", str)
FTP_USERNAME = env_var("FTP_USERNAME", str)
FTP_PASSWORD = env_var("FTP_PASSWORD", str)

#
# Integrations
#

GOOGLE_API_KEY = env_var("GOOGLE_API_KEY", str)
GOOGLE_CLIENT_ID = env_var("GOOGLE_CLIENT_ID", str)
GOOGLE_PLACE_ID = env_var("GOOGLE_PLACE_ID", str)

MOLLIE_API_KEY = env_var("MOLLIE_API_KEY", str)

INTIME_ENABLED = False

#
# Structured data
#

META_BRAND_NAME = None
META_WEBSITE_NAME = None
META_LOGO_URL = None
META_FAVICON_URL = None
META_COLOR_HEX = None

SOCIAL_DISCORD = None
SOCIAL_FACEBOOK = None
SOCIAL_INSTAGRAM = None
SOCIAL_PINTEREST = None
SOCIAL_TWITTER = None
SOCIAL_YOUTUBE = None

#
# Business information
# NOTE: these will be used in official documents
#

BUSINESS_NAME = None
BUSINESS_EMAIL = None
BUSINESS_LOGO_URL = None
BUSINESS_REGISTRATION_NUMBER = None
BUSINESS_VAT_NUMBER = None
BUSINESS_VAT_REVERSE_RATE = Decimal("1")
BUSINESS_STREET = None
BUSINESS_CITY = None
BUSINESS_ZIP_CODE = None
BUSINESS_COUNTRY = None
BUSINESS_COUNTRY_CODE = None
