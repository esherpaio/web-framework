from sqlalchemy import JSON, Boolean, Column, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from web.helper.objects import none_aware_attrgetter

from . import Base
from ._utils import FKRestrict, default_price
from ._validation import set_slug
from .product_media import ProductMedia
from .product_type import ProductTypeId


class Product(Base):
    __tablename__ = "product"

    attributes = Column(JSON)
    file_url = Column(String(128))
    html = Column(Text)
    is_deleted = Column(Boolean, nullable=False, default=False)
    name = Column(String(64), nullable=False)
    read_html = Column(Boolean, nullable=False, default=False)
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

    @set_slug("name")
    def validate_slug(self, *args) -> str:
        pass

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
