from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import OrderStatus
from webshop.database.seeds import order_status_seeds
from webshop.seeder.abc import Syncer


class OrderStatusSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in order_status_seeds:
            row = s.query(OrderStatus).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with Conn.begin() as s_:
        OrderStatusSyncer().sync(s_)
