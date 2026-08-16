import re
from enum import StrEnum

from flask import current_app, has_request_context, request

from web.setup import config


class LocaleStyle(StrEnum):
    SLUG = "slug"
    BCP47 = "bcp47"


def get_route_locale() -> str | None:
    """Get the locale for the current route."""
    if has_request_context() and request.view_args is not None:
        locale = request.view_args.get("_locale", None)
        if locale is None or None in match_locale(locale):
            return None
        return locale
    return None


def expects_locale(endpoint: str | None) -> bool:
    if endpoint is not None and current_app.url_map.is_endpoint_expecting(
        endpoint, "_locale"
    ):
        return True
    return False


def lacks_locale(endpoint: str | None, values: dict) -> bool:
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
    language_code: str | None = None,
    country_code: str | None = None,
    *,
    style: LocaleStyle = LocaleStyle.SLUG,
) -> str:
    if language_code is None:
        language_code = config.LOCALE_LANGUAGE_CODE
    if country_code is None:
        country_code = config.LOCALE_COUNTRY_CODE

    if style == LocaleStyle.SLUG:
        language_code = language_code.lower()
        country_code = country_code.lower()
    elif style == LocaleStyle.BCP47:
        language_code = language_code.lower()
        country_code = country_code.upper()

    return f"{language_code}-{country_code}"
