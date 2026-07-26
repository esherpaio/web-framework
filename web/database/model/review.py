from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column as MC
from sqlalchemy.orm import relationship, validates

from ._base import IntBase
from ._utils import get_text, val_length, val_number
from .review_status import ReviewStatusId


class Review(IntBase):
    __tablename__ = "review"

    author_name = MC(String(128), nullable=True)
    body = MC(Text, nullable=True)
    photo_url = MC(String(256), nullable=True)
    rating = MC(Integer, nullable=False)
    show_photo = MC(Boolean, nullable=False, default=True, server_default="true")
    title = MC(String(128), nullable=True)

    order_id = MC(ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id = MC(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    sku_id = MC(ForeignKey("sku.id", ondelete="CASCADE"), nullable=False)
    status_id = MC(
        ForeignKey("review_status.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    user_id = MC(ForeignKey("user.id", ondelete="SET NULL"))

    order = relationship("Order")
    product = relationship("Product")
    sku = relationship("Sku", lazy="joined")
    status = relationship("ReviewStatus", lazy="joined")
    user = relationship("User")

    # Validation

    @validates("author_name", "title")
    def validate_text(self, key: str, value: Any) -> Any:
        value = get_text(value)
        val_length(key, value, min_=1, max_=128)
        return value

    @validates("body")
    def validate_body(self, key: str, value: Any) -> Any:
        value = get_text(value)
        val_length(key, value, min_=1)
        return value

    @validates("rating")
    def validate_rating(self, key: str, value: Any) -> Any:
        val_number(key, value, min_=1, max_=5)
        return value

    # Properties - statuses

    @hybrid_property
    def is_pending(self) -> bool:
        return self.status_id == ReviewStatusId.PENDING

    @hybrid_property
    def is_approved(self) -> bool:
        return self.status_id == ReviewStatusId.APPROVED

    @hybrid_property
    def is_rejected(self) -> bool:
        return self.status_id == ReviewStatusId.REJECTED

    # Properties - general

    @hybrid_property
    def option_labels(self) -> list[str]:
        return [f"{d.option.name}: {d.value.name}" for d in self.sku.details]
