import re

from flask import current_app, request

from web import config


def set_locale(data: dict, locale: str = config.WEBSITE_LOCALE) -> None:
    """Set the locale."""

    data["_locale"] = locale


def cur_locale() -> str | None:
    """Get the locale."""

    if request.endpoint:
        if "_locale" in request.view_args:
            return request.view_args["_locale"]


def expects_locale(endpoint: str | None) -> bool:
    """Determine whether a locale is expected."""

    if endpoint:
        if current_app.url_map.is_endpoint_expecting(endpoint, "_locale"):
            return True
    return False


def requires_locale(endpoint: str | None, values: dict) -> bool:
    """Determine whether a locale is expected and not present."""

    return expects_locale(endpoint) and "_locale" not in values


def match_locale(locale: str) -> tuple[str | None, str | None]:
    """Match a locale and return the result."""

    match = re.fullmatch(r"^([a-z]{2})-([a-z]{2})$", locale)
    if match:
        return match.groups()
    else:
        return None, None


def gen_locale(
    language_code: str = config.WEBSITE_LANGUAGE_CODE,
    country_code: str = config.BUSINESS_COUNTRY_CODE,
) -> str:
    """Generate a locale using a language code and country code.

    Both codes are compliant with ISO standards.
    - Language ISO 639-1: https://simple.wikipedia.org/wiki/ISO_639-1.
    - Country ISO 3166: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes.
    """

    return f"{language_code}-{country_code}".lower()
