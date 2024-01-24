from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import OrderStatus
from web.database.seeds import order_status_seeds
from web.seeder.abc import Syncer


class OrderStatusSyncer(Syncer):
    def __init__(self, seeds: list[OrderStatus] = order_status_seeds) -> None:
        super().__init__()
        self.seeds: list[OrderStatus] = seeds

    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in self.seeds:
            row = s.query(OrderStatus).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        OrderStatusSyncer().sync(s_)
