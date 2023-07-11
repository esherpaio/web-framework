import os

from flask import url_for
from mollie.api.client import Client

from web import config


class Mollie(Client):
    """Mollie API wrapper."""

    def __init__(self):
        super().__init__()
        self.set_api_key(config.MOLLIE_KEY)


def mollie_amount(number: int | float, currency: str) -> dict:
    """Format an amount for Mollie."""

    return {"value": f"{number:.2f}", "currency": currency}


def mollie_webhook() -> str | None:
    """Get the webhook URL for Mollie."""

    if not config.LOCALHOST:
        webhook = url_for("webhook_v1.mollie_payment", _external=True)
    else:
        webhook = os.path.join(config.LOCALHOST, "webhook_v1", "mollie", "payment")
    return webhook
