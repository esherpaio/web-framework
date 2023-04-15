from sqlalchemy.orm import joinedload, Session

from webshop.database.client import conn
from webshop.database.model import Sku, SkuDetail
from webshop.seeder.abc import Syncer


class SkuSyncer(Syncer):
    def sync(self, s: Session) -> None:
        # Query all skus
        with conn.begin() as s:
            skus = (
                s.query(Sku)
                .options(
                    joinedload(Sku.product),
                    joinedload(Sku.details),
                    joinedload(Sku.details, SkuDetail.value),
                )
                .all()
            )

            # Iterate over skus
            # Calculate the unit price
            for sku in skus:
                unit_price = sku.product.unit_price
                for sku_detail in sku.details:
                    unit_price += sku_detail.value.unit_price
                sku.unit_price = unit_price
                s.flush()


if __name__ == "__main__":
    with conn.begin() as s_:
        SkuSyncer().sync(s_)
