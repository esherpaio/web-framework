import xml.etree.ElementTree as ET

import requests
from requests import RequestException

from web.automation.fixture import currency_seeds
from web.database import conn
from web.database.model import Currency
from web.logger import log
from web.setup import config

from ..automator import ApiSyncer, SeedSyncer
from ..utils import external_sync


class CurrencySeedSyncer(SeedSyncer):
    MODEL = Currency
    KEY = "id"
    SEEDS = currency_seeds


class CurrencyApiSyncer(ApiSyncer):
    API_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

    @classmethod
    @external_sync
    def run(cls) -> None:
        with conn.begin() as s:
            # Call API
            try:
                resource = requests.request(
                    "GET",
                    cls.API_URL,
                    timeout=config.AUTOMATE_TIMEOUT_S,
                )
            except RequestException as error:
                log.error(error, exc_info=True)
                return
            # Load currencies
            currencies = s.query(Currency).all()
            # Get resources data
            data = []
            tree = ET.ElementTree(ET.fromstring(resource.text))
            for el in tree.iter():
                if (
                    el.tag.endswith("Cube")
                    and "currency" in el.attrib
                    and "rate" in el.attrib
                ):
                    code = el.attrib["currency"]
                    rate = el.attrib["rate"]
                    data.append((code, rate))
            # Update currencies
            for code, rate in data:
                currency = next((x for x in currencies if x.code == code), None)
                if currency:
                    currency.rate = rate
                    s.flush()
