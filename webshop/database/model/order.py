from sqlalchemy import Column, String, Boolean, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship

from . import Base
from ._utils import price, vat, FKCascade, FKRestrict
from .order_status import OrderStatusId


class Order(Base):
    __tablename__ = "order"
    __table_args__ = (
        CheckConstraint("shipment_price >= 0"),
        CheckConstraint("total_price >= 0"),
        CheckConstraint("vat_rate >= 1"),
    )

    mollie_id = Column(String(64), unique=True)
    shipment_price = Column(price, nullable=False, default=0)
    total_price = Column(price, nullable=False)
    vat_rate = Column(vat, nullable=False)
    vat_reverse = Column(Boolean, nullable=False, default=False)

    access_id = Column(FKRestrict("access.id"), nullable=False)
    billing_id = Column(FKCascade("billing.id"))
    coupon_id = Column(FKRestrict("coupon.id"))
    currency_id = Column(FKRestrict("currency.id"), nullable=False)
    invoice_id = Column(FKRestrict("invoice.id"))
    shipment_method_id = Column(FKRestrict("shipment_method.id"))
    shipping_id = Column(FKCascade("shipping.id"))
    status_id = Column(
        FKRestrict("order_status.id"), nullable=False, default=OrderStatusId.PENDING
    )

    access = relationship("Access")
    billing = relationship("Billing")
    coupon = relationship("Coupon")
    currency = relationship("Currency")
    invoice = relationship("Invoice")
    lines = relationship("OrderLine", back_populates="order")
    refunds = relationship("Refund", back_populates="order")
    shipment_method = relationship("ShipmentMethod")
    shipments = relationship("Shipment", back_populates="order")
    shipping = relationship("Shipping")
    status = relationship("OrderStatus")

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
        self, include_vat: bool, with_coupon: bool = False, with_shipment: bool = False
    ) -> float:
        price_ = 0
        # Add order lines
        for line in self.lines:
            if include_vat:
                price_ += line.total_price_vat
            else:
                price_ += line.total_price
        # Add coupon
        if with_coupon and self.coupon:
            if self.coupon.rate:
                price_ *= self.coupon.rate
            if self.coupon.amount:
                if include_vat:
                    price_ -= self.coupon.amount * self.vat_rate
                else:
                    price_ -= self.coupon.amount
        # Add shipment
        if with_shipment:
            if include_vat:
                price_ += self.shipment_price_vat
            else:
                price_ += self.shipment_price
        return price_
