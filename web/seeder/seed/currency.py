import requests
from bs4 import BeautifulSoup
from requests import RequestException
from sqlalchemy.orm import Session

from web.database.model import Currency
from web.database.seed import currency_seeds
from web.libs.logger import log
from web.seeder import Syncer, external_seed


class CurrencySyncer(Syncer):
    MODEL = Currency
    KEY = "id"
    SEEDS = currency_seeds

    @classmethod
    @external_seed
    def sync(cls, s: Session) -> None:
        # Insert seeds
        super().sync(s)

        # Call API
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        try:
            resource = requests.request("GET", url, timeout=2)
        except RequestException as error:
            log.critical(error)
            return

        # Load currencies
        currencies = s.query(Currency).all()

        # Get resource details
        soup = BeautifulSoup(resource.text, features="xml")
        elements = soup.find_all("Cube", currency=True, rate=True)
        for element in elements:
            try:
                code = element["currency"]
                rate = element["rate"]
            except KeyError as error:
                log.critical(error)
                return

            # Update currency
            currency = next((x for x in currencies if x.code == code), None)
            if currency:
                currency.rate = rate
                s.flush()
