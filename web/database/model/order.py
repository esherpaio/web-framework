from typing import Any

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web.libs.cache import cache

from . import Base
from ._utils import default_price, default_rate, default_vat
from ._validation import get_upper, val_length, val_number
from .order_status import OrderStatusId


class Order(Base):
    __tablename__ = "order"
    __table_args__ = (CheckConstraint("coupon_amount IS NULL OR coupon_rate IS NULL"),)

    coupon_code = MC(String(32))
    coupon_amount = MC(default_price)
    coupon_rate = MC(default_rate)
    mollie_id = MC(String(64), unique=True)
    shipment_name = MC(String(64))
    shipment_price = MC(default_price, nullable=False)
    total_price = MC(default_price, nullable=False)
    vat_rate = MC(default_vat, nullable=False)
    vat_reverse = MC(Boolean, nullable=False)

    billing_id = MC(ForeignKey("billing.id", ondelete="RESTRICT"), nullable=False)
    currency_id = MC(ForeignKey("currency.id", ondelete="RESTRICT"), nullable=False)
    shipping_id = MC(ForeignKey("shipping.id", ondelete="RESTRICT"), nullable=False)
    status_id = MC(ForeignKey("order_status.id", ondelete="RESTRICT"), nullable=False)
    user_id = MC(ForeignKey("user.id", ondelete="RESTRICT"), nullable=False)

    billing = relationship("Billing")
    currency = relationship("Currency", lazy="joined")
    invoice = relationship("Invoice", uselist=False, back_populates="order")
    lines = relationship("OrderLine", back_populates="order", lazy="joined")
    refunds = relationship("Refund", back_populates="order")
    shipments = relationship("Shipment", back_populates="order")
    shipping = relationship("Shipping")
    status = relationship("OrderStatus")
    user = relationship("User")

    # Validation

    @validates("coupon_code")
    def validate_coupon_code(self, key: str, value: Any) -> Any:
        val_length(value, min_=2)
        value = get_upper(value)
        return value

    @validates("coupon_amount")
    def validate_coupon_amount(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value

    @validates("coupon_rate")
    def validate_coupon_rate(self, key: str, value: Any) -> Any:
        val_number(value, min_=0, max_=1)
        return value

    @validates("shipment_price")
    def validate_shipment_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value

    @validates("total_price")
    def validate_total_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value

    @validates("vat_rate")
    def validate_vat_rate(self, key: str, value: Any) -> Any:
        val_number(value, min_=1, max_=2)
        return value

    # Properties - statuses

    @hybrid_property
    def is_pending(self) -> bool:
        return self.status_id == OrderStatusId.PENDING

    @hybrid_property
    def is_paid(self) -> bool:
        return self.status_id == OrderStatusId.PAID

    @hybrid_property
    def is_in_progress(self) -> bool:
        return self.status_id == OrderStatusId.IN_PROGRESS

    @hybrid_property
    def is_ready(self) -> bool:
        return self.status_id == OrderStatusId.READY

    @hybrid_property
    def is_completed(self) -> bool:
        return self.status_id == OrderStatusId.COMPLETED

    @hybrid_property
    def next_statuses(self) -> list:
        if self.is_paid:
            ids = [OrderStatusId.IN_PROGRESS, OrderStatusId.READY]
        elif self.is_in_progress:
            ids = [OrderStatusId.READY]
        else:
            ids = []
        return [x for x in cache.order_statuses if x.id in ids]

    # Properties - refund

    @hybrid_property
    def remaining_refund_amount(self) -> float:
        refunded = 0.0
        for refund in self.refunds:
            refunded += abs(refund.total_price)
        remaining = self.total_price - refunded
        if remaining < 0:
            remaining = 0.0
        return remaining

    @hybrid_property
    def is_refundable(self) -> bool:
        return self.invoice and self.remaining_refund_amount > 0

    # Properties - pricing

    @hybrid_property
    def vat_percentage(self) -> int:
        return round((self.vat_rate - 1) * 100)

    @hybrid_property
    def vat_amount(self) -> float:
        return self.total_price_vat - self.total_price

    @hybrid_property
    def subtotal_price(self) -> float:
        return self._get_price(include_vat=False)

    @hybrid_property
    def subtotal_price_vat(self) -> float:
        return self._get_price(include_vat=True)

    @hybrid_property
    def discount_price(self) -> float:
        subtotal = self._get_price(include_vat=False)
        total = self._get_price(include_vat=False, with_coupon=True)
        return total - subtotal

    @hybrid_property
    def discount_price_vat(self) -> float:
        subtotal = self._get_price(include_vat=True)
        total = self._get_price(include_vat=True, with_coupon=True)
        return total - subtotal

    @hybrid_property
    def shipment_price_vat(self) -> float:
        return self.shipment_price * self.vat_rate

    @hybrid_property
    def total_price_vat(self) -> float:
        return self._get_price(include_vat=True, with_coupon=True, with_shipment=True)

    # Functions - pricing

    @hybrid_method
    def _get_price(
        self,
        include_vat: bool,
        with_coupon: bool = False,
        with_shipment: bool = False,
    ) -> float:
        price_ = 0.0
        # Add order lines
        for line in self.lines:
            if include_vat:
                price_ += line.total_price_vat
            else:
                price_ += line.total_price
        # Add coupon
        if with_coupon:
            if self.coupon_rate:
                price_ *= self.coupon_rate
            if self.coupon_amount:
                if include_vat:
                    price_ -= self.coupon_amount * self.vat_rate
                else:
                    price_ -= self.coupon_amount
        # Add shipment
        if with_shipment:
            if include_vat:
                price_ += self.shipment_price_vat
            else:
                price_ += self.shipment_price
        return price_
