from sqlalchemy.orm import Session, joinedload

from web.database import conn
from web.database.model import Sku, SkuDetail

from ..syncer import Syncer


class SkuSyncer(Syncer):
    @classmethod
    def run(cls, s: Session) -> None:
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
