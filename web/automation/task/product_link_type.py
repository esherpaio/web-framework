from web.automation.fixture import product_link_type_seeds
from web.database.model import ProductLinkType

from ..automator import SeedSyncer


class ProductLinkeTypeSeedSyncer(SeedSyncer):
    MODEL = ProductLinkType
    KEY = "id"
    SEEDS = product_link_type_seeds
