import requests
from requests import RequestException

from web.config import config
from web.database import conn
from web.database.model import Country, Currency, CurrencyId, Region
from web.logger import log

from ..automator import ApiSyncer
from ..utils import external_sync


class CountryApiSyncer(ApiSyncer):
    API_URL = "https://restcountries.com/v3.1/all?fields=name,cca2,region,currencies"

    @classmethod
    @external_sync
    def run(cls) -> None:
        cls.log_start()
        with conn.begin() as s:
            # Call API
            try:
                response = requests.request(
                    "GET",
                    cls.API_URL,
                    timeout=config.APP_SYNC_TIMEOUT_S,
                )
                resources = response.json()
            except RequestException as error:
                log.error(f"Country seeder failed: {error}")
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
                    log.error(error, exc_info=True)
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
                    log.error(error, exc_info=True)
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
