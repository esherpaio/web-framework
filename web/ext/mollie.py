import urllib.parse

from flask import url_for
from mollie.api.client import Client

from web.config import config
from web.libs.parse import strip_scheme


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
