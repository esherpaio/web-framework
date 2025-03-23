from web.automation.fixture import order_status_seeds
from web.database.model import OrderStatus

from ..automator import SeedSyncer


class OrderStatusSeedSyncer(SeedSyncer):
    MODEL = OrderStatus
    KEY = "id"
    SEEDS = order_status_seeds
