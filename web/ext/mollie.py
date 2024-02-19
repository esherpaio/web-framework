import urllib.parse

from flask import url_for
from mollie.api.client import Client

from web.config import config
from web.libs.parse import strip_scheme

#
# Classes
#


class Mollie(Client):
    """Mollie API wrapper."""

    def __init__(self):
        super().__init__()
        self.set_api_key(config.MOLLIE_KEY)


#
# Functions
#


def mollie_amount(number: int | float, currency: str) -> dict:
    """Format an amount for Mollie."""
    return {"value": f"{number:.2f}", "currency": currency}


def mollie_webhook() -> str | None:
    """Get the webhook URL for Mollie."""
    url = url_for(config.ENDPOINT_MOLLIE, _external=True, _scheme="https")
    if config.LOCALHOST:
        localhost = strip_scheme(config.LOCALHOST)
        parsed = urllib.parse.urlparse(url)
        replaced = parsed._replace(netloc=localhost)
        url = urllib.parse.urlunparse(replaced)
    return url
