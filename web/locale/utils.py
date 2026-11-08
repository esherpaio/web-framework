import functools
import re
from enum import StrEnum
from importlib.resources import files

from babel import Locale as BabelLocale
from flask import current_app, has_request_context, request

from web.cache import cache
from web.setup import config


class LocaleStyle(StrEnum):
    SLUG = "slug"
    BCP47 = "bcp47"


class Region(StrEnum):
    EUROPE = "Europe"
    ASIA = "Asia"
    AFRICA = "Africa"
    AMERICAS = "Americas"
    OCEANIA = "Oceania"
    OTHER = "Other"


ZONE_REGIONS = {
    "Europe": Region.EUROPE,
    "Asia": Region.ASIA,
    "Africa": Region.AFRICA,
    "America": Region.AMERICAS,
    "Australia": Region.OCEANIA,
    "Pacific": Region.OCEANIA,
}


def get_route_locale() -> str | None:
    if has_request_context() and request.view_args is not None:
        locale = request.view_args.get("_locale", None)
        if locale is None or None in parse_locale(locale):
            return None
        return locale
    return None


def expects_locale(endpoint: str | None) -> bool:
    return endpoint is not None and current_app.url_map.is_endpoint_expecting(
        endpoint, "_locale"
    )


def lacks_locale(endpoint: str | None, values: dict) -> bool:
    if expects_locale(endpoint):
        locale = values.get("_locale", None)
        if locale is None or None in parse_locale(locale):
            return True
    return False


def parse_locale(locale: str) -> tuple[str | None, str | None]:
    match = re.fullmatch(r"^([a-zA-Z]{2})[-_]+([a-zA-Z]{2})$", locale)
    if match is not None:
        language_code, country_code = match.groups()
        return language_code.lower(), country_code.lower()
    return None, None


def unknown_locale(locale: str | None) -> bool:
    if locale is None:
        return False
    language_code, country_code = parse_locale(locale)
    if language_code is None or country_code is None:
        return False
    if not cache.countries or not cache.languages:  # type: ignore [attr-defined]
        return False
    if not any(x.code.lower() == country_code for x in cache.countries):  # type: ignore [attr-defined]
        return True
    if not any(x.code.lower() == language_code for x in cache.languages):  # type: ignore [attr-defined]
        return True
    return False


def gen_locale(
    language_code: str | None = None,
    country_code: str | None = None,
    *,
    style: LocaleStyle = LocaleStyle.SLUG,
) -> str:
    if language_code is None:
        language_code = config.BASE_LANGUAGE_CODE
    if country_code is None:
        country_code = config.BASE_COUNTRY_CODE

    if style == LocaleStyle.SLUG:
        language_code = language_code.lower()
        country_code = country_code.lower()
    elif style == LocaleStyle.BCP47:
        language_code = language_code.lower()
        country_code = country_code.upper()

    return f"{language_code}-{country_code}"


def get_country_name(country_code: str, language_code: str | None = None) -> str:
    if language_code is None:
        language_code = config.BASE_LANGUAGE_CODE
    territories = BabelLocale(language_code).territories
    return territories.get(country_code, country_code)


@functools.cache
def get_country_regions() -> dict[str, Region]:
    regions: dict[str, Region] = {}
    zone_tab = files("tzdata.zoneinfo").joinpath("zone.tab")
    for line in zone_tab.read_text(encoding="ascii").splitlines():
        if line.startswith("#"):
            continue
        code, _, zone, *_ = line.split("\t")
        prefix = zone.partition("/")[0]
        # zone.tab lists each country's most populous zone first
        regions.setdefault(code, ZONE_REGIONS.get(prefix, Region.OTHER))
    return regions


def get_country_region(country_code: str) -> Region:
    return get_country_regions().get(country_code.upper(), Region.OTHER)
