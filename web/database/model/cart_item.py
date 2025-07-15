from decimal import Decimal
from typing import Any

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web.setup import config

from ._base import IntBase
from ._utils import val_number


class CartItem(IntBase):
    __tablename__ = "cart_item"
    __table_args__ = (UniqueConstraint("cart_id", "sku_id"),)

    quantity = MC(Integer, nullable=False)

    cart_id = MC(ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    sku_id = MC(ForeignKey("sku.id", ondelete="RESTRICT"), nullable=False)

    cart = relationship("Cart", back_populates="items", lazy="joined")
    sku = relationship("Sku", lazy="joined")

    # Validations

    @validates("quantity")
    def validate_quantity(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=1)
        return value

    # Properties - pricing

    @hybrid_property
    def unit_price(self) -> Decimal:
        unit_price = self.sku.unit_price
        if self.cart.vat_reverse:
            vat_rate = Decimal(str(config.BUSINESS_VAT_REVERSE_RATE))
            unit_price *= vat_rate
        return unit_price * self.cart.currency.rate

    @hybrid_property
    def unit_price_vat(self) -> Decimal:
        return self.unit_price * self.cart.vat_rate

    @hybrid_property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

    @hybrid_property
    def total_price_vat(self) -> Decimal:
        return self.total_price * self.cart.vat_rate

    # Properties - SKU

    @hybrid_property
    def sku_name(self) -> str:
        return self.sku.name
