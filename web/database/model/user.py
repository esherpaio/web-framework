from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Attribute, Base
from ._utils import get_lower, val_email
from .user_role import UserRoleId


class User(Base, Attribute):
    __tablename__ = "user"

    api_key = MC(String(64), unique=True)
    bulk_email = MC(Boolean, nullable=False, default=True, server_default="true")
    email = MC(String(128), unique=True)
    is_active = MC(Boolean, nullable=False, default=False, server_default="false")
    password_hash = MC(String(256))

    billing_id = MC(ForeignKey("billing.id", ondelete="CASCADE"))
    role_id = MC(ForeignKey("user_role.id", ondelete="RESTRICT"), nullable=False)
    shipping_id = MC(ForeignKey("shipping.id", ondelete="CASCADE"))

    billing = relationship("Billing", foreign_keys=[billing_id])
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    role = relationship("UserRole")
    shipping = relationship("Shipping", foreign_keys=[shipping_id])
    verifications = relationship("Verification", back_populates="user")

    # Validation

    @validates("email")
    def validate_email(self, key: str, value: Any) -> Any:
        val_email(value)
        value = get_lower(value)
        return value

    # Properties - roles

    @hybrid_property
    def is_guest(self) -> bool:
        return self.role_id == UserRoleId.GUEST

    @hybrid_property
    def is_user(self) -> bool:
        return self.role_id == UserRoleId.USER

    @hybrid_property
    def is_admin(self) -> bool:
        return self.role_id == UserRoleId.ADMIN

    @hybrid_property
    def is_super(self) -> bool:
        return self.role_id == UserRoleId.SUPER

    # Flask mixin

    @property
    def is_authenticated(self) -> bool:
        return (not self.is_guest) and self.is_active

    @property
    def is_anonymous(self) -> bool:
        return self.is_guest

    def get_id(self) -> int | None:
        return self.id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            if not self.is_guest:
                return self.get_id() == other.get_id()
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
