from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import ProductType
from web.database.seeds import product_type_seeds
from web.seeder.abc import Syncer


class ProductTypeSyncer(Syncer):
    def __init__(self, seeds: list[ProductType] = product_type_seeds) -> None:
        super().__init__()
        self.seeds: list[ProductType] = seeds

    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in self.seeds:
            row = s.query(ProductType).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        ProductTypeSyncer().sync(s_)
