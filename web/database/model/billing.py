from typing import Any

from sqlalchemy import Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

from web.database.model import Base

from ._utils import FKCascade, FKRestrict
from ._validation import del_emoji, get_lower, val_email, val_length, val_phone


class Billing(Base):
    __tablename__ = "billing"

    address = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    company = Column(String(64))
    email = Column(String(64), nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    phone = Column(String(64))
    vat = Column(String(64))
    zip_code = Column(String(64), nullable=False)

    country_id = Column(FKRestrict("country.id"), nullable=False)
    user_id = Column(FKCascade("user.id", use_alter=True), nullable=False)

    country = relationship("Country", lazy="joined")

    # Validation

    @validates("address", "city", "zip_code", "company", "first_name", "last_name")
    def validate_address(self, key: str, value: Any) -> Any:
        val_length(value, min_=2)
        value = del_emoji(value)
        return value

    @validates("email")
    def validate_email(self, key: str, value: Any) -> Any:
        val_email(value)
        value = get_lower(value)
        return value

    @validates("phone")
    def validate_phone(self, key: str, value: Any) -> Any:
        val_phone(value)
        return value

    # Properties - general

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def full_address(self) -> str:
        return f"{self.address}, {self.zip_code} {self.city}, {self.country.name}"
