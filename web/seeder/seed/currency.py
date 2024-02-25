import requests
from bs4 import BeautifulSoup
from requests import RequestException
from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import Currency
from web.database.seed import currency_seeds
from web.libs.logger import log
from web.seeder.abc import Syncer
from web.seeder.decorators import external_seed


class CurrencySyncer(Syncer):
    def __init__(self, seeds: list[Currency] = currency_seeds) -> None:
        super().__init__()
        self.seeds: list[Currency] = seeds

    @external_seed
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in self.seeds:
            row = s.query(Currency).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()

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


if __name__ == "__main__":
    with conn.begin() as s_:
        CurrencySyncer().sync(s_)
