from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict, FKSetNull
from ._validation import check_email
from .user_role import UserRoleId


class User(Base):
    __tablename__ = "user"

    email = Column(String(64), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=False)
    password_hash = Column(String(256), nullable=False)

    billing_id = Column(FKSetNull("billing.id"))
    role_id = Column(
        FKRestrict("user_role.id"), nullable=False, default=UserRoleId.USER
    )
    shipping_id = Column(FKSetNull("shipping.id"))

    access = relationship("Access", back_populates="user")
    billing = relationship("Billing")
    role = relationship("UserRole")
    shipping = relationship("Shipping")
    verifications = relationship("UserVerification", back_populates="user")

    # Validation

    @check_email("email")
    def validate_email(self, *args) -> str:
        pass

    # Properties - roles

    @hybrid_property
    def is_user(self) -> bool:
        return self.role_id == UserRoleId.USER

    @hybrid_property
    def is_admin(self) -> bool:
        return self.role_id == UserRoleId.ADMIN

    @hybrid_property
    def is_super(self) -> bool:
        return self.role_id == UserRoleId.SUPER
