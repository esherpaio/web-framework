import os

from flask import url_for
from mollie.api.client import Client

from web import config


class Mollie(Client):
    def __init__(self):
        super().__init__()
        self.set_api_key(config.MOLLIE_KEY)


def mollie_amount(number: int | float, currency: str) -> dict:
    return {"value": f"{number:.2f}", "currency": currency}


def mollie_webhook() -> str | None:
    if not config.LOCALHOST:
        webhook = url_for("webhook.mollie_payment", _external=True)
    else:
        webhook = os.path.join(config.LOCALHOST, "webhook", "mollie", "payment")
    return webhook
