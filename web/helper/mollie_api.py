import os

from flask import url_for
from mollie.api.client import Client

from web import config

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
    if not config.LOCALHOST:
        webhook = url_for(config.ENDPOINT_MOLLIE, _external=True)
    else:
        # TODO: this should not be hardcoded
        webhook = os.path.join(config.LOCALHOST, "webhook", "v1", "mollie", "payment")
    return webhook
