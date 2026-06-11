from web.database import conn
from web.database.model import Region
from web.logger import log

from ..automator import RestCountriesApiSyncer
from ..utils import external_sync


class RegionApiSyncer(RestCountriesApiSyncer):
    API_URL = (
        "https://api.restcountries.com/countries/v5?response_fields=region&limit=100"
    )

    @classmethod
    @external_sync
    def run(cls) -> None:
        cls.log_start()
        with conn.begin() as s:
            try:
                resources = cls.fetch_all(cls.API_URL)
            except Exception as error:
                log.error(error, exc_info=True)
                return

            regions = s.query(Region).all()
            region_names = set(x["region"] for x in resources if x.get("region"))
            for region_name in region_names:
                region = next((x for x in regions if x.name == region_name), None)
                if region is not None:
                    continue
                s.add(Region(name=region_name))
                s.flush()
