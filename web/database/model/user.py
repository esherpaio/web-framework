from typing import Any

from sqlalchemy import JSON, Boolean, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, validates

from . import Base
from ._utils import FKCascade, FKRestrict
from ._validation import get_lower, val_email
from .user_role import UserRoleId


class FlaskUserMixin:
    @property
    def is_authenticated(self) -> bool:
        return not self.is_guest and self.is_active

    @property
    def is_anonymous(self) -> bool:
        return self.is_guest

    def get_id(self) -> int:
        return self.id

    def __eq__(self, other: "FlaskUserMixin") -> bool:
        if self.is_guest:
            return False
        return self.get_id() == other.get_id()

    def __ne__(self, other: "FlaskUserMixin") -> bool:
        return not self.__eq__(other)


class User(Base, FlaskUserMixin):
    __tablename__ = "user"

    api_key = Column(String(64), unique=True)
    attributes = Column(
        MutableDict.as_mutable(JSON), nullable=False, server_default="{}"
    )
    email = Column(String(64), unique=True)
    is_active = Column(Boolean, nullable=False, default=False)
    password_hash = Column(String(256))

    billing_id = Column(FKCascade("billing.id"))
    role_id = Column(FKRestrict("user_role.id"), nullable=False)
    shipping_id = Column(FKCascade("shipping.id"))

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
