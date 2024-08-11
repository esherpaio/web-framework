import requests
from requests import RequestException
from sqlalchemy.orm import Session

from web.config import config
from web.database.model import Region
from web.logger import log

from ..syncer import Syncer
from ..utils import external_sync


class RegionSyncer(Syncer):
    @classmethod
    @external_sync
    def run(cls, s: Session) -> None:
        # Call API
        url = "https://restcountries.com/v3.1/all?fields=region"
        try:
            response = requests.request("GET", url, timeout=config.APP_SYNC_TIMEOUT)
            resources = response.json()
        except RequestException as error:
            log.critical(error)
            return

        # Load regions
        regions = s.query(Region).all()

        # Get all region names
        try:
            region_names = set(x["region"] for x in resources)
        except KeyError as error:
            log.critical(error)
            return

        # Insert regions
        for region_name in region_names:
            region = next((x for x in regions if x.name == region_name), None)
            if not region:
                s.add(Region(name=region_name))
                s.flush()
