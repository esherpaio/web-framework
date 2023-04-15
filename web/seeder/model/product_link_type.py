from sqlalchemy.orm import Session

from web.database.client import conn
from web.database.model import ProductLinkType
from web.database.seeds import product_link_type_seeds
from web.seeder.abc import Syncer


class ProductLinkeTypeSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in product_link_type_seeds:
            row = s.query(ProductLinkType).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        ProductLinkeTypeSyncer().sync(s_)
