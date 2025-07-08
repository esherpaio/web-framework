from decimal import ROUND_HALF_UP, Decimal

from mollie.api.client import Client

from web.app.urls import url_for
from web.logger import log
from web.setup import settings
from web.utils.modifiers import replace_domain


class Mollie(Client):
    def __init__(self) -> None:
        super().__init__()
        if settings.MOLLIE_API_KEY is not None:
            self.set_api_key(settings.MOLLIE_API_KEY)
        else:
            log.warning("Mollie API key is not set")

    @property
    def webhook_url(self) -> str:
        url = url_for("webhook_v1.mollie_payment", _external=True, _scheme="https")
        if settings.LOCALHOST_URL:
            url = replace_domain(url, settings.LOCALHOST_URL)
        return url

    @property
    def supported_locales(self) -> list[str]:
        return [
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

    @staticmethod
    def gen_amount(value: Decimal, currency: str) -> dict:
        quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {"value": str(quantized), "currency": currency}
