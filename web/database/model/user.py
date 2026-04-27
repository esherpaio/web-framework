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
    bulk_email = MC(Boolean, nullable=False, default=False, server_default="false")
    newsletter_email = MC(
        Boolean, nullable=False, default=False, server_default="false"
    )

    role_id = MC(
        ForeignKey("user_role.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    role = relationship("UserRole")
    verifications = relationship("Verification", back_populates="user")
    default_billing = relationship(
        "Billing",
        primaryjoin=("and_(User.id == Billing.user_id, Billing.is_default.is_(True))"),
        foreign_keys="Billing.user_id",
        uselist=False,
        viewonly=True,
    )
    default_shipping = relationship(
        "Shipping",
        primaryjoin=(
            "and_(User.id == Shipping.user_id, Shipping.is_default.is_(True))"
        ),
        foreign_keys="Shipping.user_id",
        uselist=False,
        viewonly=True,
    )

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

    # Properties - defaults

    @property
    def default_billing_id(self) -> int | None:
        return self.default_billing.id if self.default_billing is not None else None

    @property
    def default_shipping_id(self) -> int | None:
        return self.default_shipping.id if self.default_shipping is not None else None
