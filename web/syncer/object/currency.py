import xml.etree.ElementTree as ET

import requests
from requests import RequestException
from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Currency
from web.database.seed import currency_seeds
from web.libs.logger import log

from ..syncer import Syncer
from ..utils import external_sync


class CurrencySyncer(Syncer):
    MODEL = Currency
    KEY = "id"
    SEEDS = currency_seeds

    @classmethod
    @external_sync
    def sync(cls, s: Session) -> None:
        # Insert seeds
        super().sync(s)

        # Call API
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        try:
            resource = requests.request("GET", url, timeout=config.APP_SYNC_TIMEOUT)
        except RequestException as error:
            log.critical(error)
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
