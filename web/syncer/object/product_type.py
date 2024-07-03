from web.database.model import ProductType
from web.database.seed import product_type_seeds

from .. import Syncer


class ProductTypeSyncer(Syncer):
    MODEL = ProductType
    KEY = "id"
    SEEDS = product_type_seeds
