from sqlalchemy import Boolean, CheckConstraint, Column
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKCascade, FKRestrict, price, vat


class Cart(Base):
    __tablename__ = "cart"
    __table_args__ = (
        CheckConstraint("shipment_price >= 0"),
        CheckConstraint("vat_rate >= 1"),
    )

    shipment_price = Column(price, nullable=False, default=0)
    vat_rate = Column(vat, nullable=False, default=1)
    vat_reverse = Column(Boolean, nullable=False, default=False)

    access_id = Column(FKCascade("access.id"), nullable=False, unique=True)
    billing_id = Column(FKRestrict("billing.id"))
    coupon_id = Column(FKRestrict("coupon.id"))
    currency_id = Column(FKRestrict("currency.id"), nullable=False)
    shipment_method_id = Column(FKRestrict("shipment_method.id"))
    shipping_id = Column(FKRestrict("shipping.id"))

    access = relationship("Access")
    billing = relationship("Billing")
    coupon = relationship("Coupon")
    currency = relationship("Currency", lazy="joined")
    items = relationship("CartItem", back_populates="cart")
    shipment_method = relationship("ShipmentMethod")
    shipping = relationship("Shipping")

    # Properties - general

    @hybrid_property
    def items_count(self) -> int:
        if self.items:
            return len(self.items)
        return 0

    # Properties - pricing

    @hybrid_property
    def vat_percentage(self) -> int:
        return round((self.vat_rate - 1) * 100)

    @hybrid_property
    def vat_amount(self) -> float:
        return self.total_price_vat - self.total_price

    @hybrid_property
    def subtotal_price(self) -> float:
        return self._calc_price(include_vat=False)

    @hybrid_property
    def subtotal_price_vat(self) -> float:
        return self._calc_price(include_vat=True)

    @hybrid_property
    def discount_price(self) -> float:
        subtotal = self._calc_price(include_vat=False)
        total = self._calc_price(include_vat=False, with_coupon=True)
        return total - subtotal

    @hybrid_property
    def discount_price_vat(self) -> float:
        subtotal = self._calc_price(include_vat=True)
        total = self._calc_price(include_vat=True, with_coupon=True)
        return total - subtotal

    @hybrid_property
    def shipment_price_vat(self) -> float:
        return self.shipment_price * self.vat_rate

    @hybrid_property
    def total_price(self) -> float:
        return self._calc_price(include_vat=False, with_coupon=True, with_shipment=True)

    @hybrid_property
    def total_price_vat(self) -> float:
        return self._calc_price(include_vat=True, with_coupon=True, with_shipment=True)

    # Functions - pricing

    @hybrid_method
    def _calc_price(
        self, include_vat: bool, with_coupon: bool = False, with_shipment: bool = False
    ) -> float:
        price_ = 0
        # Add order lines
        for item in self.items:
            if include_vat:
                price_ += item.total_price_vat
            else:
                price_ += item.total_price
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
