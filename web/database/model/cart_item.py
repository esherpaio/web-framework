from typing import Any

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web import config

from . import Base
from ._validation import val_number


class CartItem(Base):
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
        val_number(value, min_=1)
        return value

    # Properties - pricing

    @hybrid_property
    def unit_price(self) -> float:
        unit_price = self.sku.unit_price
        if self.cart.vat_reverse:
            unit_price *= config.BUSINESS_VAT_RATE
        return unit_price * self.cart.currency.rate

    @hybrid_property
    def unit_price_vat(self) -> float:
        return self.unit_price * self.cart.vat_rate

    @hybrid_property
    def total_price(self) -> float:
        return self.unit_price * self.quantity

    @hybrid_property
    def total_price_vat(self) -> float:
        return self.total_price * self.cart.vat_rate
