from datetime import datetime
from functools import cached_property

from babel.dates import format_datetime

from web.cache import cache
from web.database.model import Country, Currency, Language
from web.setup import settings

from .error import CountryNotFoundError, CurrencyNotFoundError, LanguageNotFoundError
from .utils import gen_locale, get_cookie_locale, get_route_locale, match_locale


class Locale:
    """A class for handling locale information.

    If you want to use locales in routes, it is expected that you use the
    "_locale" variable. For example "/<string:_locale>/home". Because we
    keep URLs always in lowercase, the locale will be in lowercase as well.
    """

    @property
    def possible_locales(self) -> list[str]:
        locales = []
        view_locale = get_route_locale()
        if view_locale:
            locales.append(view_locale)
        cookie_locale = get_cookie_locale()
        if cookie_locale:
            locales.append(cookie_locale)
        web_locale = gen_locale(
            settings.LOCALE_LANGUAGE_CODE, settings.LOCALE_COUNTRY_CODE
        )
        locales.append(web_locale)
        return locales

    @cached_property
    def locale(self) -> str:
        return f"{self.language_code.lower()}-{self.country_code.lower()}"

    @cached_property
    def locale_posix(self) -> str:
        return f"{self.language_code.lower()}_{self.country_code.upper()}"

    #
    # Codes
    #

    @property
    def possible_language_codes(self) -> list[str]:
        possible_language_codes = []
        for possible_locale in self.possible_locales:
            possible_language_code = match_locale(possible_locale)[0]
            if possible_language_code is not None:
                possible_language_codes.append(possible_language_code.lower())
        return possible_language_codes

    @cached_property
    def language_code(self) -> str:
        try:
            return self.language.code
        except Exception:
            return settings.LOCALE_LANGUAGE_CODE

    @property
    def possible_country_codes(self) -> list[str]:
        possible_country_codes = []
        for possible_locale in self.possible_locales:
            possible_country_code = match_locale(possible_locale)[1]
            if possible_country_code is not None:
                possible_country_codes.append(possible_country_code.upper())
        return possible_country_codes

    @cached_property
    def country_code(self) -> str:
        try:
            return self.country.code
        except Exception:
            return settings.LOCALE_COUNTRY_CODE

    #
    # Objects
    #

    @cached_property
    def language(self) -> Language:
        for language_code in self.possible_language_codes:
            language = next(
                (x for x in cache.languages if x.code == language_code),  # type: ignore[attr-defined]
                None,
            )
            if language is not None:
                return language
        raise LanguageNotFoundError

    @cached_property
    def country(self) -> Country:
        for country_code in self.possible_country_codes:
            country = next(
                (x for x in cache.countries if x.code == country_code),  # type: ignore[attr-defined]
                None,
            )
            if country is not None:
                return country
        raise CountryNotFoundError

    @cached_property
    def currency(self) -> Currency:
        currency_id = self.country.currency_id
        for currency in cache.currencies:  # type: ignore[attr-defined]
            if currency.id == currency_id:
                return currency
        raise CurrencyNotFoundError

    #
    # Functions
    #

    def format_datetime(self, datetime_: datetime) -> str:
        return format_datetime(datetime_, locale=self.locale_posix)
