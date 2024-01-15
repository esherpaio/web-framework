from typing import Any

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web.database.model import Base

from ._validation import del_emoji, get_lower, val_email, val_length, val_phone


class Billing(Base):
    __tablename__ = "billing"

    address = MC(String(64), nullable=False)
    city = MC(String(64), nullable=False)
    company = MC(String(64))
    email = MC(String(64), nullable=False)
    first_name = MC(String(64), nullable=False)
    last_name = MC(String(64), nullable=False)
    phone = MC(String(64))
    state = MC(String(64))
    vat = MC(String(64))
    zip_code = MC(String(64), nullable=False)

    country_id = MC(ForeignKey("country.id", ondelete="RESTRICT"), nullable=False)
    user_id = MC(
        ForeignKey("user.id", ondelete="CASCADE", use_alter=True), nullable=False
    )

    country = relationship("Country", lazy="joined")

    # Validation

    @validates(
        "address", "city", "state", "zip_code", "company", "first_name", "last_name"
    )
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

    @full_name.expression  # type: ignore
    def full_name(cls):
        return func.concat(cls.first_name, " ", cls.last_name)

    @hybrid_property
    def full_address(self) -> str:
        return f"{self.address}, {self.zip_code} {self.city}, {self.country.name}"
