import os
from decimal import Decimal

# Application
# NOTE: keep the secret key used in production secret
# NOTE: do not run with debug turned on in production

APP_ROOT: str = os.path.dirname(os.path.abspath(__file__))
APP_LOG_LEVEL: str = "INFO"
APP_DEBUG: bool = True
APP_DEBUG_PORT: int = 5000
APP_URL_SCHEME: str = "http"
APP_OPTIMIZE: bool = False
APP_SYNC_EXTERNAL: bool = True
APP_SYNC_STATIC: bool = True
APP_SYNC_TIMEOUT_S: int = 10

WORKER_ENABLED: bool = False
WORKER_INTERVAL_S: int = 300

# Authentication

AUTH_JWT_COOKIE_NAME: str = "access_token"
AUTH_JWT_ENCODE_ALGORITHM: str = "HS256"
AUTH_JWT_DECODE_ALGORITHMS: list[str] = ["HS256"]
AUTH_JWT_SECRET: str = "secret"
AUTH_JWT_ALLOW_GUEST: bool = False
AUTH_JWT_EXPIRES_S: int = 86400
AUTH_JWT_DECODE_LEEWAY_S: int = 0

AUTH_KEY_HEADER_NAME: str = "Authorization"

AUTH_CSRF_COOKIE_NAME: str = "csrf_token"
AUTH_CSRF_METHODS: list[str] = ["POST", "PUT", "PATCH", "DELETE"]

# Endpoints

ENDPOINT_HOME: None | str = None
ENDPOINT_ERROR: None | str = None
ENDPOINT_LOGIN: None | str = None
ENDPOINT_PASSWORD_RECOVERY: None | str = None

# Integrations

DATABASE_URL: None | str = None
LOCALHOST_URL: None | str = None

MOLLIE_KEY: None | str = None

GOOGLE_KEY: None | str = None
GOOGLE_CLIENT_ID: None | str = None
GOOGLE_PLACE_ID: None | str = None

INTIME_INTEGRATION: bool = False

# Content delivery network

CDN_URL: None | str = None
CDN_HOSTNAME: None | str = None
CDN_USERNAME: None | str = None
CDN_PASSWORD: None | str = None

CDN_AUTO_NAMING: bool = False
CDN_IMAGE_EXTS: list[str] = ["jpg", "jpeg", "png", "webp"]
CDN_AUDIO_EXTS: list[str] = ["m4a", "mp3", "mp4"]
CDN_VIDEO_EXTS: list[str] = ["mp4"]

# Email configuration

EMAIL_METHOD: str = "SMTP"
EMAIL_TIMEOUT_S: int = 10
EMAIL_MAX_RECIPIENTS: int = 100
EMAIL_FROM: None | str = None
EMAIL_TO: None | str = None
EMAIL_ADMIN: None | str = None

SMTP_HOSTNAME: None | str = None
SMTP_PORT: int = 587
SMTP_USERNAME: None | str = None
SMTP_PASSWORD: None | str = None

# Website details

WEBSITE_NAME: None | str = None
WEBSITE_COUNTRY_CODE: None | str = None
WEBSITE_LANGUAGE_CODE: None | str = None
WEBSITE_FAVICON_URL: None | str = None
WEBSITE_LOGO_URL: None | str = None
WEBSITE_HEX_COLOR: None | str = None

# Business details

BUSINESS_NAME: None | str = None
BUSINESS_EMAIL: None | str = None
BUSINESS_CC: None | str = None
BUSINESS_VAT: None | str = None
BUSINESS_VAT_RATE: Decimal = Decimal("1")
BUSINESS_VAT_REVERSE_CHARGE: bool = False
BUSINESS_STREET: None | str = None
BUSINESS_CITY: None | str = None
BUSINESS_ZIP_CODE: None | str = None
BUSINESS_COUNTRY: None | str = None
BUSINESS_COUNTRY_CODE: None | str = None

# Social media links

SOCIAL_DISCORD: None | str = None
SOCIAL_FACEBOOK: None | str = None
SOCIAL_INSTAGRAM: None | str = None
SOCIAL_PINTEREST: None | str = None
SOCIAL_TWITTER: None | str = None
SOCIAL_YOUTUBE: None | str = None
