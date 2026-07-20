import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, event, insert, select
from sqlalchemy.engine import Connection
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapper, relationship, validates
from sqlalchemy.orm import mapped_column as MC

from web.setup import config

from ._base import IntBase
from ._utils import get_text, val_length, val_number
from .order import Order
from .order_status import OrderStatusId
from .review_status import ReviewStatusId
from .verification import Verification, VerificationType


class Review(IntBase):
    __tablename__ = "review"

    author_name = MC(String(128), nullable=False)
    body = MC(Text, nullable=False)
    photo_url = MC(String(256))
    rating = MC(Integer, nullable=False)
    show_photo = MC(Boolean, nullable=False, default=True, server_default="true")
    title = MC(String(128), nullable=False)

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


@event.listens_for(Order, "after_insert")
@event.listens_for(Order, "after_update")
def _create_review_request(
    mapper: Mapper,
    connection: Connection,
    target: Order,
) -> None:
    if not config.REVIEW_ENABLED:
        return
    if target.status_id != OrderStatusId.COMPLETED:
        return

    delay_days = config.REVIEW_REQUEST_DELAY_DAYS or 14
    expires_days = config.REVIEW_REQUEST_EXPIRES_DAYS or 90
    now = datetime.now(UTC)
    valid_from = now + timedelta(days=delay_days)
    expires_at = valid_from + timedelta(days=expires_days)

    if expires_at < now:
        return

    existing = connection.execute(
        select(Verification.id).where(
            Verification.type == VerificationType.REVIEW,
            Verification.data["order_id"].astext == str(target.id),
        )
    ).first()
    if existing is not None:
        return

    from web.mail import enqueue_email
    from web.mail.enum import MailEvent

    token = uuid.uuid4().hex
    connection.execute(
        insert(Verification).values(
            key=token,
            type=VerificationType.REVIEW,
            user_id=target.user_id,
            valid_from=valid_from,
            expires_at=expires_at,
            data={"order_id": target.id},
        )
    )
    enqueue_email(
        connection,
        MailEvent.REVIEW_REQUEST,
        data={"token": token},
        scheduled_at=valid_from,
        user_id=target.user_id,
    )
