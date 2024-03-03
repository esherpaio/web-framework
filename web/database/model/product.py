from typing import Any

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from web.libs.utils import none_attrgetter

from ._base import Attribute, Base
from ._utils import default_price, get_slug, val_number
from .product_media import ProductMedia
from .product_type import ProductTypeId


class Product(Base, Attribute):
    __tablename__ = "product"

    file_url = MC(String(128))
    is_deleted = MC(Boolean, nullable=False, default=False, server_default="false")
    name = MC(String(64), nullable=False)
    consent_required = MC(
        Boolean, nullable=False, default=False, server_default="false"
    )
    slug = MC(String(64), unique=True, nullable=False)
    summary = MC(String(64))
    unit_price = MC(default_price, nullable=False)

    shipment_class_id = MC(ForeignKey("shipment_class.id", ondelete="RESTRICT"))
    type_id = MC(ForeignKey("product_type.id", ondelete="RESTRICT"), nullable=False)

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

    # Properties - joins

    @hybrid_property
    def shipment_class_name(self) -> str | None:
        if self.shipment_class is not None:
            return getattr(self.shipment_class, "name", None)

    # Properties - statuses

    @hybrid_property
    def is_physical(self) -> bool:
        return self.type_id == ProductTypeId.PHYSICAL

    # Properties - media

    @hybrid_property
    def images(self) -> list[ProductMedia]:
        medias = [x for x in self.medias if x.file.is_image]
        return sorted(medias, key=none_attrgetter("order"))

    @hybrid_property
    def videos(self) -> list[ProductMedia]:
        medias = [x for x in self.medias if x.file.is_video]
        return sorted(medias, key=none_attrgetter("order"))
