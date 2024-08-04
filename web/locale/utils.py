import re

from flask import current_app, has_request_context, request

from web.config import config
from web.libs.urls import url_for


def get_route_locale() -> str | None:
    """Get the locale for the current route."""
    if has_request_context() and request.view_args is not None:
        locale = request.view_args.get("_locale", None)
        if locale is None or None in match_locale(locale):
            return None
        return locale
    return None


def get_cookie_locale() -> str | None:
    """Get the locale from the cookie."""
    if has_request_context():
        locale = request.cookies.get("locale", None)
        if locale is None or None in match_locale(locale):
            return None
        return locale
    return None


def expects_locale(endpoint: str | None) -> bool:
    """Determine whether a locale is expected."""
    if endpoint is not None and current_app.url_map.is_endpoint_expecting(
        endpoint, "_locale"
    ):
        return True
    return False


def lacks_locale(endpoint: str | None, values: dict) -> bool:
    """Determine whether a locale lacks."""
    if expects_locale(endpoint):
        locale = values.get("_locale", None)
        if locale is None or None in match_locale(locale):
            return True
    return False


def match_locale(locale: str) -> tuple[str | None, ...]:
    """Parse a language and country code."""
    match = re.fullmatch(r"^([a-zA-Z]{2})[-_]+([a-zA-Z]{2})$", locale)
    if match is not None:
        language_code, country_code = match.groups()
        return language_code.lower(), country_code.lower()
    return None, None


def gen_locale(
    language_code: str | None = None, country_code: str | None = None
) -> str:
    """Generate a locale."""
    if language_code is None:
        language_code = config.WEBSITE_LANGUAGE_CODE
    if country_code is None:
        country_code = config.BUSINESS_COUNTRY_CODE
    return f"{language_code}-{country_code}".lower()


def url_for_locale(endpoint: str, *args, **kwargs) -> str:
    """Generate an URL for a route with locale."""
    if not expects_locale(endpoint) and "_locale" in kwargs:
        kwargs.pop("_locale")
    return url_for(endpoint, *args, **kwargs)
