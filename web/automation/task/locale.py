import xml.etree.ElementTree as ET
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from babel import Locale as BabelLocale
from babel.numbers import get_currency_symbol, get_territory_currencies
from pycountry import countries as iso_countries
from pycountry import languages as iso_languages
from requests import RequestException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import InstrumentedAttribute, Session

from web.database import conn
from web.database.model import AppSettings, Country, Currency, Language
from web.logger import log
from web.setup import config

from ..automator import Automator


class LocaleSyncer(Automator):
    INTERVAL_S = 86400

    COUNTRY_CODES: set[str] | None = set()
    LANGUAGE_CODES: set[str] = set()
    CURRENCY_CODES: set[str] = set()

    RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    RATES_CURRENCY_CODE = "EUR"
    FALLBACK_CURRENCY_CODE = "USD"

    @classmethod
    def run(cls) -> None:
        locale = BabelLocale(config.BASE_LANGUAGE_CODE)
        countries = cls._lookup(iso_countries, cls.COUNTRY_CODES)
        languages = cls._lookup(iso_languages, cls.LANGUAGE_CODES)
        currency_codes = cls.CURRENCY_CODES | {
            config.BASE_CURRENCY_CODE,
            cls.FALLBACK_CURRENCY_CODE,
        }
        rates = cls._get_rates()

        with conn.begin() as s:
            currencies = cls._sync_currencies(s, locale, currency_codes, rates)
            cls._sync_languages(s, locale, languages)
            cls._sync_countries(s, locale, countries, currencies)
            cls._delete_unused(s, Country.code, countries.keys())
            cls._delete_unused(s, Language.code, languages.keys())
            cls._delete_unused(s, Currency.code, currency_codes)

            settings = s.query(AppSettings).first()
            if settings is not None:
                settings.cached_at = datetime.now(UTC)

    @classmethod
    def _sync_currencies(
        cls,
        s: Session,
        locale: BabelLocale,
        codes: set[str],
        rates: dict[str, Decimal],
    ) -> dict[str, Currency]:
        missing_codes = sorted(codes - rates.keys())
        if rates and missing_codes:
            log.error(f"No ECB rates for currencies: {missing_codes}")

        rate_codes = codes & rates.keys()
        rows: dict[str, Currency] = cls._get_or_create(s, Currency.code, rate_codes)
        for code in rate_codes:
            symbol = get_currency_symbol(code, locale=locale)
            if len(symbol) > Currency.symbol.type.length:
                symbol = code
            currency = rows[code]
            currency.rate = rates[code]
            currency.symbol = symbol
        return {code: rows[code] for code in codes & rows.keys()}

    @classmethod
    def _sync_languages(
        cls,
        s: Session,
        locale: BabelLocale,
        languages: dict[str, Any],
    ) -> None:
        rows: dict[str, Language] = cls._get_or_create(
            s,
            Language.code,
            languages.keys(),
        )
        for code, entry in languages.items():
            language = rows[code]
            language.name = locale.languages.get(code, entry.name)

    @classmethod
    def _sync_countries(
        cls,
        s: Session,
        locale: BabelLocale,
        countries: dict[str, Any],
        currencies: dict[str, Currency],
    ) -> None:
        fallback_code = cls.FALLBACK_CURRENCY_CODE
        if fallback_code not in currencies:
            raise ValueError(f"Fallback currency {fallback_code} is missing")

        rows: dict[str, Country] = cls._get_or_create(s, Country.code, countries.keys())
        for code, entry in countries.items():
            territory_codes = get_territory_currencies(code)
            currency_code = next(
                (c for c in territory_codes if c in currencies),
                fallback_code,
            )
            country = rows[code]
            country.name = locale.territories.get(code, entry.name)
            country.currency = currencies[currency_code]

    @classmethod
    def _get_rates(cls) -> dict[str, Decimal]:
        try:
            response = requests.get(cls.RATES_URL, timeout=10)
            response.raise_for_status()
        except RequestException as error:
            log.error(f"Cannot fetch currency rates: {error}", exc_info=True)
            return {}

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as error:
            log.error(f"Cannot parse currency rates: {error}", exc_info=True)
            return {}

        ecb_rates = {cls.RATES_CURRENCY_CODE: Decimal(1)}
        for cube in root.iterfind(".//{*}Cube[@currency]"):
            try:
                ecb_rates[cube.attrib["currency"]] = Decimal(cube.get("rate", ""))
            except InvalidOperation:
                continue

        base_rate = ecb_rates.get(config.BASE_CURRENCY_CODE)
        if not base_rate:
            log.error(f"No ECB rate for {config.BASE_CURRENCY_CODE}")
            return {}

        rate_type = Currency.rate.type
        quantum = Decimal(10) ** -rate_type.scale
        limit = Decimal(10) ** (rate_type.precision - rate_type.scale)

        rates: dict[str, Decimal] = {}
        for code, ecb_rate in ecb_rates.items():
            rate = (ecb_rate / base_rate).quantize(quantum)
            if 0 < rate < limit:
                rates[code] = rate
        return rates

    @staticmethod
    def _lookup(database: Any, codes: set[str] | None) -> dict[str, Any]:
        if codes is None:
            return {entry.alpha_2: entry for entry in database}
        entries = {code: database.get(alpha_2=code) for code in codes}
        unknown_codes = sorted(code for code, entry in entries.items() if entry is None)
        if unknown_codes:
            raise ValueError(f"Unknown ISO codes: {', '.join(unknown_codes)}")
        return {entry.alpha_2: entry for entry in entries.values()}

    @staticmethod
    def _get_or_create(
        s: Session,
        column: InstrumentedAttribute[Any],
        codes: Iterable[str],
    ) -> dict[str, Any]:
        model = column.parent.class_
        rows = {getattr(row, column.key): row for row in s.query(model)}
        for code in codes:
            if code not in rows:
                rows[code] = model(**{column.key: code})
                s.add(rows[code])
        return rows

    @staticmethod
    def _delete_unused(
        s: Session,
        column: InstrumentedAttribute[Any],
        codes: Iterable[str],
    ) -> None:
        # Flush first so write errors are not mistaken for references
        s.flush()
        model = column.parent.class_
        for row in s.query(model).filter(column.notin_(codes)).all():
            try:
                with s.begin_nested():
                    s.delete(row)
            except IntegrityError:
                code = getattr(row, column.key)
                log.warning(f"Keeping referenced {model.__tablename__} {code}")
