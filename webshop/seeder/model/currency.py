import requests
from bs4 import BeautifulSoup
from requests import RequestException
from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import Currency
from webshop.database.seeds import currency_seeds
from webshop.helper.logger import logger
from webshop.seeder.abc import Syncer
from webshop.seeder.utils import external_seed


class CurrencySyncer(Syncer):
    @external_seed
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in currency_seeds:
            row = s.query(Currency).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()

        # Call API
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        try:
            resource = requests.request("GET", url, timeout=2)
        except RequestException as error:
            logger.critical(error)
            return

        # Load iteration objects
        currencies = s.query(Currency).all()

        # Get resource details
        soup = BeautifulSoup(resource.text, features="xml")
        elements = soup.find_all("Cube", currency=True, rate=True)
        for element in elements:
            try:
                cube_code = element["currency"]
                cube_rate = element["rate"]
            except KeyError as error:
                logger.critical(error)
                return

            # Update currency
            currency = next((x for x in currencies if x.code == cube_code), None)
            if currency:
                currency.rate = cube_rate
                s.flush()


if __name__ == "__main__":
    with Conn.begin() as s_:
        CurrencySyncer().sync(s_)
