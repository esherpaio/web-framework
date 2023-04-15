import requests
from requests import RequestException
from sqlalchemy.orm import Session

from webshop.database.client import conn
from webshop.database.model import Country, Currency, Region, CurrencyId
from webshop.helper.logger import logger
from webshop.seeder.abc import Syncer
from webshop.seeder.utils import external_seed


class CountrySyncer(Syncer):
    @external_seed
    def sync(self, s: Session) -> None:
        # Call API
        url = "https://restcountries.com/v3.1/all?fields=name,cca2,region,currencies"
        try:
            response = requests.request("GET", url, timeout=2)
            resources = response.json()
        except RequestException as error:
            logger.critical(error)
            return

        # Load iteration objects
        currencies = s.query(Currency).all()
        currency_usd = s.query(Currency).filter_by(id=CurrencyId.USD).first()
        regions = s.query(Region).all()
        countries = s.query(Country).all()

        # Get resource details
        for resource in resources:
            try:
                country_name = resource["name"]["common"]
                country_code = resource["cca2"]
                region_name = resource["region"]
                country_currency_codes = list(resource["currencies"].keys())
            except KeyError as error:
                logger.critical(error)
                continue

            # Get currency, fallback to USD
            for currency in currencies:
                if currency.code in country_currency_codes:
                    break
            else:
                currency = currency_usd

            # Get region
            try:
                region = next(x for x in regions if x.name == region_name)
            except StopIteration as error:
                logger.critical(error)
                continue

            # Update or insert country
            country = next((x for x in countries if x.code == country_code), None)
            if country:
                country.currency_id = currency.id
                country.name = country_name
                country.region_id = region.id
            else:
                country = Country(
                    code=country_code,
                    currency_id=currency.id,
                    name=country_name,
                    region_id=region.id,
                )
                s.add(country)
            s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        CountrySyncer().sync(s_)
