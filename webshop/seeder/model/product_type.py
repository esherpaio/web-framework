from sqlalchemy.orm import Session

from webshop.database.client import conn
from webshop.database.model import ProductType
from webshop.database.seeds import product_type_seeds
from webshop.seeder.abc import Syncer


class ProductTypeSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in product_type_seeds:
            row = s.query(ProductType).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        ProductTypeSyncer().sync(s_)
