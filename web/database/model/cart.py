from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Base
from ._utils import default_price, default_vat, val_number


class Cart(Base):
    __tablename__ = "cart"

    shipment_price = MC(
        default_price, nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    vat_rate = MC(default_vat, nullable=False, default=Decimal("1"), server_default="1")
    vat_reverse = MC(Boolean, nullable=False, default=False, server_default="false")

    billing_id = MC(ForeignKey("billing.id", ondelete="RESTRICT"))
    coupon_id = MC(ForeignKey("coupon.id", ondelete="RESTRICT"))
    currency_id = MC(ForeignKey("currency.id", ondelete="RESTRICT"), nullable=False)
    shipment_method_id = MC(ForeignKey("shipment_method.id", ondelete="SET NULL"))
    shipping_id = MC(ForeignKey("shipping.id", ondelete="RESTRICT"))
    user_id = MC(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)

    billing = relationship("Billing")
    coupon = relationship("Coupon", lazy="joined")
    currency = relationship("Currency", lazy="joined")
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete", lazy="joined"
    )
    shipment_method = relationship("ShipmentMethod")
    shipping = relationship("Shipping")
    user = relationship("User")

    # Validations

    @validates("shipment_price")
    def validate_shipment_price(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=0)
        return value

    @validates("vat_rate")
    def validate_vat_rate(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=1, max_=2)
        return value

    # Properties - general

    @hybrid_property
    def items_count(self) -> int:
        if self.items:
            return len(self.items)
        return 0

    # Properties - pricing

    @hybrid_property
    def currency_code(self) -> str | None:
        if self.currency:
            return self.currency.code
        return None

    @hybrid_property
    def coupon_code(self) -> str | None:
        if self.coupon:
            return self.coupon.code
        return None

    @hybrid_property
    def vat_percentage(self) -> int:
        return int(round((self.vat_rate - 1) * 100))

    @hybrid_property
    def vat_amount(self) -> Decimal:
        return self.total_price_vat - self.total_price

    @hybrid_property
    def subtotal_price(self) -> Decimal:
        return self._get_price(include_vat=False)

    @hybrid_property
    def subtotal_price_vat(self) -> Decimal:
        return self._get_price(include_vat=True)

    @hybrid_property
    def discount_price(self) -> Decimal:
        subtotal = self._get_price(include_vat=False)
        total = self._get_price(include_vat=False, with_coupon=True)
        return total - subtotal

    @hybrid_property
    def discount_price_vat(self) -> Decimal:
        subtotal = self._get_price(include_vat=True)
        total = self._get_price(include_vat=True, with_coupon=True)
        return total - subtotal

    @hybrid_property
    def shipment_price_vat(self) -> Decimal:
        return self.shipment_price * self.vat_rate

    @hybrid_property
    def total_price(self) -> Decimal:
        return self._get_price(include_vat=False, with_coupon=True, with_shipment=True)

    @hybrid_property
    def total_price_vat(self) -> Decimal:
        return self._get_price(include_vat=True, with_coupon=True, with_shipment=True)

    # Functions - pricing

    @hybrid_method
    def _get_price(
        self,
        include_vat: bool,
        with_coupon: bool = False,
        with_shipment: bool = False,
    ) -> Decimal:
        price = Decimal()
        # Add order lines
        for item in self.items:
            if include_vat:
                price += item.total_price_vat
            else:
                price += item.total_price
        # Add coupon
        if with_coupon and self.coupon:
            if self.coupon.rate:
                price *= self.coupon.rate
            if self.coupon.amount:
                if include_vat:
                    price -= self.coupon.amount * self.vat_rate
                else:
                    price -= self.coupon.amount
        # Add shipment
        if with_shipment:
            if include_vat:
                price += self.shipment_price_vat
            else:
                price += self.shipment_price
        return price
