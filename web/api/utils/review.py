import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from web.app.urls import url_for
from web.database.model import Order, Review, Verification, VerificationType
from web.mail import MailEvent, mail
from web.setup import config

if TYPE_CHECKING:
    from web.app.schema import ReviewItem


def gen_review_items(reviews: list[Review]) -> list["ReviewItem"]:
    items: list[ReviewItem] = []
    for review in reviews:
        item: ReviewItem = {
            "author": review.author_name,
            "rating": review.rating,
            "body": review.body,
            "date_published": review.created_at.date().isoformat(),
        }
        if review.title:
            item["title"] = review.title
        items.append(item)
    return items


def create_review_request(s: Session, order: Order) -> None:
    if not config.REVIEW_ENABLED:
        return

    existing = (
        s.query(Verification.id)
        .filter(
            Verification.type == VerificationType.REVIEW,
            Verification.data["order_id"].as_integer() == order.id,
        )
        .first()
    )
    if existing is not None:
        return

    now = datetime.now(UTC)
    valid_from = now + timedelta(days=config.REVIEW_REQUEST_DELAY_DAYS)
    expires_at = valid_from + timedelta(days=config.REVIEW_REQUEST_EXPIRES_DAYS)
    token = uuid.uuid4().hex
    verification = Verification(
        key=token,
        type=VerificationType.REVIEW,
        user_id=order.user_id,
        valid_from=valid_from,
        expires_at=expires_at,
        data={"order_id": order.id},
    )
    s.add(verification)
    s.flush()

    review_url = url_for("checkout.review", _external=True, token=token)
    mail.trigger_events(
        s,
        MailEvent.REVIEW_REQUEST,
        order.user_id,
        scheduled_at=valid_from,
        token=token,
        review_url=review_url,
    )
