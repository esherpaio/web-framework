from sqlalchemy import Boolean, CheckConstraint, Column, String
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict, default_price, default_rate, default_vat
from .order_status import OrderStatusId


class Order(Base):
    __tablename__ = "order"
    __table_args__ = (
        CheckConstraint("coupon_amount IS NOT NULL OR coupon_rate IS NOT NULL"),
        CheckConstraint("shipment_price >= 0"),
        CheckConstraint("total_price >= 0"),
        CheckConstraint("vat_rate >= 1"),
    )

    coupon_amount = Column(default_price)
    coupon_code = Column(String(16))
    coupon_rate = Column(default_rate)
    mollie_id = Column(String(64), unique=True)
    shipment_name = Column(String(64))
    shipment_price = Column(default_price, nullable=False)
    total_price = Column(default_price, nullable=False)
    vat_rate = Column(default_vat, nullable=False)
    vat_reverse = Column(Boolean, nullable=False)

    billing_id = Column(FKRestrict("billing.id"), nullable=False)
    currency_id = Column(FKRestrict("currency.id"), nullable=False)
    shipping_id = Column(FKRestrict("shipping.id"), nullable=False)
    status_id = Column(FKRestrict("order_status.id"), nullable=False)
    user_id = Column(FKRestrict("user.id"), nullable=False)

    billing = relationship("Billing")
    currency = relationship("Currency")
    invoice = relationship("Invoice", back_populates="order")
    lines = relationship("OrderLine", back_populates="order")
    refunds = relationship("Refund", back_populates="order")
    shipments = relationship("Shipment", back_populates="order")
    shipping = relationship("Shipping")
    status = relationship("OrderStatus")
    user = relationship("User")

    # Properties - statuses

    @hybrid_property
    def is_pending(self) -> bool:
        return self.status_id == OrderStatusId.PENDING

    @hybrid_property
    def is_paid(self) -> bool:
        return self.status_id == OrderStatusId.PAID

    @hybrid_property
    def is_production(self) -> bool:
        return self.status_id == OrderStatusId.PRODUCTION

    @hybrid_property
    def is_ready(self) -> bool:
        return self.status_id == OrderStatusId.READY

    @hybrid_property
    def is_completed(self) -> bool:
        return self.status_id == OrderStatusId.COMPLETED

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
        return self.invoice_id and self.remaining_refund_amount > 0

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
        price_ = 0
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
