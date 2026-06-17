from web.database import conn
from web.database.model import Country, Currency, Region
from web.logger import log

from ..automator import RestCountriesApiSyncer
from ..utils import external_sync


class CountryApiSyncer(RestCountriesApiSyncer):
    API_URL = "https://api.restcountries.com/countries/v5?response_fields=names,codes,region,currencies&limit=100"
    CURRENCY_CODE = "USD"

    @classmethod
    @external_sync
    def run(cls) -> None:
        cls.log_start()
        with conn.begin() as s:
            # Call API
            try:
                resources = cls.fetch_all(cls.API_URL)
            except Exception as error:
                log.error(error, exc_info=True)
                return

            # Load iteration objects
            currency_base = s.query(Currency).filter_by(code=cls.CURRENCY_CODE).first()
            if currency_base is None:
                log.warning(f"Base currency {cls.CURRENCY_CODE} not found")
                return
            currencies = s.query(Currency).all()
            regions = s.query(Region).all()
            countries = s.query(Country).all()

            # Get resource details
            for resource in resources:
                country_name = resource.get("names", {}).get("common")
                if not country_name:
                    continue
                country_code = resource.get("codes", {}).get("alpha_2")
                if not country_code:
                    continue
                region_name = resource.get("region")
                if not region_name:
                    continue
                if not isinstance(resource.get("currencies"), list):
                    continue
                currency_codes = [
                    x["code"]
                    for x in resource["currencies"]
                    if x.get("code") and len(x["code"]) == 3 and x["code"].isalpha()
                ]
                if not currency_codes:
                    continue

                # Get currency and region
                currency = next(
                    (x for x in currencies if x.code in currency_codes),
                    currency_base,
                )
                region = next((x for x in regions if x.name == region_name), None)
                if region is None:
                    continue

                # Upsert country
                country = next((x for x in countries if x.code == country_code), None)
                if country:
                    country.name = country_name
                    country.currency_id = currency.id
                    country.region_id = region.id
                else:
                    country = Country(
                        code=country_code,
                        name=country_name,
                        currency_id=currency.id,
                        region_id=region.id,
                    )
                    s.add(country)
                s.flush()
