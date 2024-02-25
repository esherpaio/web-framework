import re
from functools import cached_property
from typing import Any

from flask import current_app, g, has_request_context, request, url_for
from werkzeug.local import LocalProxy

from web.config import config
from web.database.model import Country, Currency, Language
from web.libs.cache import cache

#
# Classes
#


class Locale:
    """A class for handling locale information.

    If you want to use locales in routes, it is expected that you use the
    "_locale" variable. For example "/<string:_locale>/home". Because we
    keep URLs always in lowercase, the locale will be in lowercase as well.
    """

    @cached_property
    def locale(self) -> str:
        """Return locale in format "language-country".

        Example: "en-us" or "de-de".
        """
        view_locale = get_route_locale()
        cookie_locale = request.cookies.get("locale")
        locale = view_locale or cookie_locale or config.WEBSITE_LOCALE
        return locale

    @cached_property
    def locale_alt(self) -> str:
        """Return locale in format "language_COUNTRY".

        Example: "en_US" or "de_DE".
        """
        language_code, country_code = self.locale_info
        return f"{language_code}_{country_code}"

    @cached_property
    def locale_info(self) -> tuple[str, str]:
        """Return the language and country code.

        The language code will in be in ISO 639-1 format.
        The country code will be in ISO 3166-1 alpha-2 format.
        """
        language_code, country_code = match_locale(self.locale)
        if language_code is None:
            language_code = config.WEBSITE_LANGUAGE_CODE
        if country_code is None:
            country_code = config.BUSINESS_COUNTRY_CODE
        language_code = language_code.lower()
        country_code = country_code.upper()
        return language_code, country_code

    @cached_property
    def country(self) -> Country | None:
        _, country_code = self.locale_info
        for country in cache.countries:
            if country.code == country_code:
                return country

    @cached_property
    def currency(self) -> Currency | None:
        if self.country is None:
            return None
        currency_id = self.country.currency_id
        for currency in cache.currencies:
            if currency.id == currency_id:
                return currency

    @cached_property
    def language(self) -> Language | None:
        language_code, _ = self.locale_info
        for language in cache.languages:
            if language.code == language_code:
                return language


#
# Functions
#


def get_route_locale() -> str | None:
    """Get the locale for the current route."""
    if has_request_context() and request.endpoint:
        if request.view_args is not None and "_locale" in request.view_args:
            return request.view_args["_locale"]


def expects_locale(endpoint: str | None) -> bool:
    """Determine whether a locale is expected for the current route."""
    if endpoint:
        if current_app.url_map.is_endpoint_expecting(endpoint, "_locale"):
            return True
    return False


def lacks_locale(endpoint: str | None, values: dict) -> bool:
    """Determine whether a locale lacks for the current route."""
    return expects_locale(endpoint) and "_locale" not in values


def match_locale(locale: str) -> tuple[str | None, ...]:
    """Return the language and country code for a locale."""
    match = re.fullmatch(r"^([a-z]{2})-([a-z]{2})$", locale)
    if match:
        return match.groups()
    return None, None


def gen_locale(
    language_code: str = config.WEBSITE_LANGUAGE_CODE,
    country_code: str = config.BUSINESS_COUNTRY_CODE,
) -> str:
    """Generate a locale using a language code and country code."""
    return f"{language_code}-{country_code}".lower()


def url_for_locale(endpoint: str, *args, **kwargs) -> str:
    """Generate an URL for a route with locale."""
    if not expects_locale(endpoint) and "_locale" in kwargs:
        kwargs.pop("_locale")
    return url_for(endpoint, *args, **kwargs)


def _get_proxy_locale() -> Locale | None:
    if has_request_context():
        if "_locale" not in g:
            g._locale = Locale()
        return g._locale


#
# Variables
#


current_locale: Any = LocalProxy(lambda: _get_proxy_locale())
