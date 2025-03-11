from datetime import datetime
from functools import cached_property

from babel.dates import format_datetime

from web.cache import cache
from web.config import config
from web.database.model import Country, Currency, Language

from .error import CountryNotFoundError, CurrencyNotFoundError, LanguageNotFoundError
from .utils import gen_locale, get_cookie_locale, get_route_locale, match_locale


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
        cookie_locale = get_cookie_locale()
        website_locale = gen_locale(
            config.WEBSITE_LANGUAGE_CODE, config.WEBSITE_COUNTRY_CODE
        )
        return view_locale or cookie_locale or website_locale

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

    #
    # Objects
    #

    @cached_property
    def country(self) -> Country:
        _, country_code = self.locale_info
        for country in cache.countries:  # type: ignore[attr-defined]
            if country.code == country_code:
                return country
        raise CountryNotFoundError

    @cached_property
    def currency(self) -> Currency:
        currency_id = self.country.currency_id
        for currency in cache.currencies:  # type: ignore[attr-defined]
            if currency.id == currency_id:
                return currency
        raise CurrencyNotFoundError

    @cached_property
    def language(self) -> Language:
        language_code, _ = self.locale_info
        for language in cache.languages:  # type: ignore[attr-defined]
            if language.code == language_code:
                return language
        raise LanguageNotFoundError

    #
    # Functions
    #

    def format_datetime(self, datetime_: datetime) -> None:
        format_datetime(datetime_, locale=self.locale_alt)
