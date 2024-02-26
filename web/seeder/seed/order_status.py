from web.database.model import OrderStatus
from web.database.seed import order_status_seeds
from web.seeder import Syncer


class OrderStatusSyncer(Syncer):
    MODEL = OrderStatus
    KEY = "id"
    SEEDS = order_status_seeds
