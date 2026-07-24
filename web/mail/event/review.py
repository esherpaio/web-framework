from sqlalchemy.orm import Session

from web.database.model import Order, Verification, VerificationType
from web.i18n import _
from web.setup import config

from .. import render_email, send_email


def mail_review_request(
    s: Session,
    token: str,
    review_url: str,
    **kwargs,
) -> bool:
    verification = (
        s.query(Verification).filter_by(key=token, type=VerificationType.REVIEW).first()
    )
    if verification is None or not verification.is_valid:
        return False
    order = s.query(Order).filter_by(id=verification.data.get("order_id")).first()
    if order is None:
        return False

    subject = _("MAIL_REVIEW_SUBJECT", business_name=config.BUSINESS_NAME)
    html = render_email(
        title=_("MAIL_REVIEW_TITLE"),
        paragraphs=[
            _("MAIL_REVIEW_P1", business_name=config.BUSINESS_NAME),
            _("MAIL_REVIEW_P2", review_url=review_url),
            _("MAIL_REVIEW_P3"),
        ],
    )
    return send_email(subject, html, to=[order.billing.email])
