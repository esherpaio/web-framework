from sqlalchemy.orm import Session

from webshop.database.client import Conn
from webshop.database.model import ProductLinkType
from webshop.database.seeds import product_link_type_seeds
from webshop.seeder.abc import Syncer


class ProductLinkeTypeSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Insert seeds
        for seed in product_link_type_seeds:
            row = s.query(ProductLinkType).filter_by(id=seed.id).first()
            if not row:
                s.add(seed)
                s.flush()


if __name__ == "__main__":
    with Conn.begin() as s_:
        ProductLinkeTypeSyncer().sync(s_)
