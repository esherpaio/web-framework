import requests
from requests import RequestException
from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model.region import Region
from webshop.helper.logger import logger
from webshop.helper.seeder import external_seed, Syncer


class RegionSyncer(Syncer):
    @external_seed
    def sync(self, s: Session) -> None:
        url = "https://restcountries.com/v3.1/all?fields=region"
        try:
            response = requests.request("GET", url, timeout=2)
            resources = response.json()
        except RequestException as error:
            logger.critical(error)
            return

        # Load iteration objects
        regions = s.query(Region).all()

        # Get all region names
        try:
            region_names = set(x["region"] for x in resources)
        except KeyError as error:
            logger.critical(error)
            return

        # Insert regions
        for region_name in region_names:
            region_is_europe = region_name == "Europe"
            region = next((x for x in regions if x.name == region_name), None)
            if not region:
                region = Region(name=region_name, is_europe=region_is_europe)
                s.add(region)
                s.flush()


if __name__ == "__main__":
    with Conn.begin() as s_:
        RegionSyncer().sync(s_)
