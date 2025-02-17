import urllib.parse
from datetime import datetime, timedelta, timezone

from mollie.api.client import Client
from sqlalchemy.orm.session import Session

from web.app.urls import url_for
from web.config import config
from web.database.model import Order
from web.locale import current_locale

LOCALES = [
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


def get_mollie_webhook_url() -> str | None:
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


def gen_mollie_amount(number: int | float, currency: str) -> dict:
    return {"value": f"{number:.2f}", "currency": currency}


def gen_mollie_payment_data(
    s: Session,
    order: Order,
    redirect_url: str,
    cancel_url: str,
    methods: None | list[str] = None,
) -> dict:
    order_price_vat = order.total_price * order.vat_rate
    amount = gen_mollie_amount(order_price_vat, order.currency_code)
    description = f"Order {order.id}"
    due_date = datetime.now(timezone.utc) + timedelta(days=25)
    due_data_str = due_date.strftime("%Y-%m-%d")
    data = {
        "amount": amount,
        "description": description,
        "redirectUrl": redirect_url,
        "cancelUrl": cancel_url,
        "webhookUrl": get_mollie_webhook_url(),
        "metadata": {"order_id": order.id},
        "dueDate": due_data_str,
    }
    if current_locale.locale_alt in LOCALES:
        data["locale"] = current_locale.locale_alt
    if methods:
        data["method"] = methods
    return data
