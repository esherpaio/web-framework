import requests
from requests import RequestException

from web.database import conn
from web.database.model import Region
from web.logger import log
from web.setup import config

from ..automator import ApiSyncer
from ..utils import external_sync


class RegionApiSyncer(ApiSyncer):
    API_URL = "https://restcountries.com/v3.1/all?fields=region"

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
                    timeout=config.AUTOMATE_TIMEOUT_S,
                )
                resources = response.json()
            except RequestException as error:
                log.error(error, exc_info=True)
                return
            # Load regions
            regions = s.query(Region).all()
            # Get all region names
            try:
                region_names = set(x["region"] for x in resources)
            except KeyError as error:
                log.error(error, exc_info=True)
                return
            # Insert regions
            for region_name in region_names:
                region = next((x for x in regions if x.name == region_name), None)
                if not region:
                    s.add(Region(name=region_name))
                    s.flush()
