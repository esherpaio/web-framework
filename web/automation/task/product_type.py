from web.automation.fixture import product_type_seeds
from web.database.model import ProductType

from ..automator import SeedSyncer


class ProductTypeSeedSyncer(SeedSyncer):
    MODEL = ProductType
    KEY = "id"
    SEEDS = product_type_seeds
