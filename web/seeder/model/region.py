import requests
from requests import RequestException
from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import Region
from web.helper.logger import logger
from web.seeder.abc import Syncer
from web.seeder.decorators import external_seed


class RegionSyncer(Syncer):
    @external_seed
    def sync(self, s: Session) -> None:
        # Call API
        url = "https://restcountries.com/v3.1/all?fields=region"
        try:
            response = requests.request("GET", url, timeout=2)
            resources = response.json()
        except RequestException as error:
            logger.critical(error)
            return

        # Load regions
        regions = s.query(Region).all()

        # Get all region names
        try:
            region_names = set(x["region"] for x in resources)
        except KeyError as error:
            logger.critical(error)
            return

        # Insert regions
        for region_name in region_names:
            region = next((x for x in regions if x.name == region_name), None)
            if not region:
                s.add(Region(name=region_name))
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        RegionSyncer().sync(s_)
