from sqlalchemy import Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from . import Base
from ._utils import FKRestrict
from ._validation import check_email, check_phone, check_str_len


class Shipping(Base):
    __tablename__ = "shipping"

    address = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    company = Column(String(64))
    email = Column(String(64), nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    phone = Column(String(64))
    zip_code = Column(String(64), nullable=False)

    country_id = Column(FKRestrict("country.id"), nullable=False)

    country = relationship("Country", lazy="joined")

    # Validation

    @check_str_len(
        2, "address", "city", "zip_code", "company", "first_name", "last_name"
    )
    def validate_location(self, *args) -> str:
        pass

    @check_email("email")
    def validate_email(self, *args) -> str:
        pass

    @check_phone("phone")
    def validate_phone(self, *args) -> str:
        pass

    # Properties - general

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def full_address(self) -> str:
        return f"{self.address}, {self.zip_code} {self.city}, {self.country.name}"
