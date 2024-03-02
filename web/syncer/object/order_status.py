from web.database.model import OrderStatus
from web.database.seed import order_status_seeds
from web.syncer import Syncer


class OrderStatusSyncer(Syncer):
    MODEL = OrderStatus
    KEY = "id"
    SEEDS = order_status_seeds
