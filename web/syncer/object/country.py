import requests
from requests import RequestException
from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Country, Currency, CurrencyId, Region
from web.libs.logger import log

from ..base import Syncer
from ..utils import external_sync


class CountrySyncer(Syncer):
    @classmethod
    @external_sync
    def sync(cls, s: Session) -> None:
        # Call API
        url = "https://restcountries.com/v3.1/all?fields=name,cca2,region,currencies"
        try:
            response = requests.request("GET", url, timeout=config.APP_SYNC_TIMEOUT)
            resources = response.json()
        except RequestException as error:
            log.critical(f"Country seeder failed: {error}")
            return

        # Load iteration objects
        currencies = s.query(Currency).all()
        currency_usd = s.query(Currency).filter_by(id=CurrencyId.USD).first()
        regions = s.query(Region).all()
        countries = s.query(Country).all()

        # Sanity checks
        if currency_usd is None:
            log.warning("Country seeder failed: USD currency not found")
            return

        # Get resource details
        for resource in resources:
            try:
                country_name = resource["name"]["common"]
                country_code = resource["cca2"]
                region_name = resource["region"]
                currency_codes = list(resource["currencies"].keys())
            except KeyError as error:
                log.critical(error)
                continue

            # Get currency, fallback to USD
            for currency in currencies:
                if currency.code in currency_codes:
                    break
            else:
                currency = currency_usd

            # Get region
            try:
                region = next(x for x in regions if x.name == region_name)
            except StopIteration as error:
                log.critical(error)
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
