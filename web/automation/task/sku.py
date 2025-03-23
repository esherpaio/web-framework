from sqlalchemy.orm import joinedload

from web.database import conn
from web.database.model import Sku, SkuDetail

from ..automator import Processor


class SkuProcessor(Processor):
    @classmethod
    def run(cls) -> None:
        cls.log_start()
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
            for sku in skus:
                unit_price = sku.product.unit_price + sum(
                    x.value.unit_price for x in sku.details
                )
                sku.unit_price = unit_price
                s.flush()
