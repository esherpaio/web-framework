import urllib.parse

from mollie.api.client import Client

from web.app.urls import url_for
from web.config import config

DEFAULT_LOCALE = "en_US"
VALID_LOCALES = [
    "ca_ES",
    "da_DK",
    "de_AT",
    "de_CH",
    "de_DE",
    "en_GB",
    "en_US",
    "es_ES",
    "fi_FI",
    "fr_BE",
    "fr_FR",
    "hu_HU",
    "is_IS",
    "it_IT",
    "lt_LT",
    "lv_LV",
    "nb_NO",
    "nl_BE",
    "nl_NL",
    "pl_PL",
    "pt_PT",
    "sv_SE",
]


class Mollie(Client):
    def __init__(self) -> None:
        super().__init__()
        self.set_api_key(config.MOLLIE_KEY)


def mollie_amount(number: int | float, currency: str) -> dict:
    return {"value": f"{number:.2f}", "currency": currency}


def mollie_webhook() -> str | None:
    url = url_for("webhook_v1.mollie_payment", _external=True, _scheme="https")
    if config.LOCALHOST:
        localhost = strip_scheme(config.LOCALHOST)
        parsed = urllib.parse.urlparse(url)
        replaced = parsed._replace(netloc=localhost)
        url = urllib.parse.urlunparse(replaced)
    return url


def strip_scheme(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    scheme = f"{parsed.scheme}://"
    return parsed.geturl().replace(scheme, "", 1)
