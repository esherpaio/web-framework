import re

from flask import current_app, has_request_context, request, url_for

from web.config import config


def get_route_locale() -> str | None:
    """Get the locale for the current route."""
    if has_request_context() and request.endpoint:
        if request.view_args is not None and "_locale" in request.view_args:
            return request.view_args["_locale"]
    return None


def expects_locale(endpoint: str | None) -> bool:
    """Determine whether a locale is expected."""
    if endpoint:
        if current_app.url_map.is_endpoint_expecting(endpoint, "_locale"):
            return True
    return False


def lacks_locale(endpoint: str | None, values: dict) -> bool:
    """Determine whether a locale lacks."""
    return expects_locale(endpoint) and "_locale" not in values


def match_locale(locale: str) -> tuple[str | None, ...]:
    """Parse a language and country code."""
    match = re.fullmatch(r"^([a-zA-Z]{2})[-_]+([a-zA-Z]{2})$", locale)
    if match:
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
