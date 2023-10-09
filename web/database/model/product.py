from typing import Any

from sqlalchemy import JSON, Boolean, Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, validates

from web.helper.builtins import none_aware_attrgetter

from . import Base
from ._utils import FKRestrict, default_price
from ._validation import get_slug, val_number
from .product_media import ProductMedia
from .product_type import ProductTypeId


class Product(Base):
    __tablename__ = "product"

    attributes = Column(
        MutableDict.as_mutable(JSON), nullable=False, server_default="{}"
    )
    file_url = Column(String(128))
    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    consent_required = Column(Boolean, nullable=False, default=False)
    slug = Column(String(64), unique=True, nullable=False)
    summary = Column(String(64))
    unit_price = Column(default_price, nullable=False)

    shipment_class_id = Column(FKRestrict("shipment_class.id"))
    type_id = Column(FKRestrict("product_type.id"), nullable=False)

    links = relationship("ProductLink", back_populates="product")
    medias = relationship(
        "ProductMedia", back_populates="product", order_by="ProductMedia.order"
    )
    options = relationship(
        "ProductOption", back_populates="product", order_by="ProductOption.order"
    )
    shipment_class = relationship("ShipmentClass")
    type = relationship("ProductType")

    # Validation

    @validates("name")
    def validate_name(self, key: str, value: Any) -> Any:
        self.slug = get_slug(value)
        return value

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Any) -> Any:
        val_number(value, min_=0)
        return value

    # Properties - statuses

    @hybrid_property
    def is_physical(self) -> bool:
        return self.type_id == ProductTypeId.PHYSICAL

    # Properties - media

    @hybrid_property
    def images(self) -> list[ProductMedia]:
        medias = [x for x in self.medias if x.file.is_image]
        return sorted(medias, key=none_aware_attrgetter("order"))

    @hybrid_property
    def videos(self) -> list[ProductMedia]:
        medias = [x for x in self.medias if x.file.is_video]
        return sorted(medias, key=none_aware_attrgetter("order"))
