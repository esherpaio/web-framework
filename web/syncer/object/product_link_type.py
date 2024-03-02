from web.database.model import ProductLinkType
from web.database.seed import product_link_type_seeds
from web.syncer import Syncer


class ProductLinkeTypeSyncer(Syncer):
    MODEL = ProductLinkType
    KEY = "id"
    SEEDS = product_link_type_seeds
