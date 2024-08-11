from web.automation.seed import order_status_seeds
from web.database.model import OrderStatus

from .. import Syncer


class OrderStatusSyncer(Syncer):
    MODEL = OrderStatus
    KEY = "id"
    SEEDS = order_status_seeds
