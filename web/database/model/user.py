from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import Attribute, IntBase
from ._utils import get_lower, val_email
from .user_role import UserRoleId


class User(IntBase, Attribute):
    __tablename__ = "user"

    display_name = MC(String(128))
    api_key = MC(String(64), unique=True)
    email = MC(String(128), unique=True)
    is_active = MC(Boolean, nullable=False, default=False, server_default="false")
    password_hash = MC(String(256))
    bulk_email = MC(Boolean, nullable=False, default=True, server_default="true")
    newsletter_email = MC(Boolean, nullable=False, default=True, server_default="true")

    billing_id = MC(ForeignKey("billing.id", ondelete="CASCADE"))
    role_id = MC(
        ForeignKey("user_role.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
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
