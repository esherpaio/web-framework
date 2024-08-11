from web.automation.seed import product_link_type_seeds
from web.database.model import ProductLinkType

from .. import Syncer


class ProductLinkeTypeSyncer(Syncer):
    MODEL = ProductLinkType
    KEY = "id"
    SEEDS = product_link_type_seeds
