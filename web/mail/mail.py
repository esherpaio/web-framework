from datetime import datetime
from enum import StrEnum
from typing import Callable

from sqlalchemy.orm import Session

from web.auth import current_user
from web.config import config
from web.database.model import Email, EmailStatusId
from web.logger import log
from web.utils import Singleton

from .event import (
    mail_bulk,
    mail_contact_business,
    mail_order_paid,
    mail_order_received,
    mail_order_refunded,
    mail_order_shipped,
    mail_user_password,
    mail_user_verification,
)


class MailError(Exception):
    pass


class MailEvent(StrEnum):
    ORDER_PAID = "order.paid"
    ORDER_RECEIVED = "order.received"
    ORDER_REFUNDED = "order.refunded"
    ORDER_SHIPPED = "order.shipped"
    USER_REQUEST_PASSWORD = "user.request_password"
    USER_REQUEST_VERIFICATION = "user.request_verification"
    WEBSITE_CONTACT = "website.contact"
    WEBSITE_BULK = "website.bulk"


class Mail(metaclass=Singleton):
    events: dict[MailEvent | str, list[Callable]] = {
        MailEvent.ORDER_PAID: [mail_order_paid],
        MailEvent.ORDER_RECEIVED: [mail_order_received],
        MailEvent.ORDER_REFUNDED: [mail_order_refunded],
        MailEvent.ORDER_SHIPPED: [mail_order_shipped],
        MailEvent.USER_REQUEST_PASSWORD: [mail_user_password],
        MailEvent.USER_REQUEST_VERIFICATION: [mail_user_verification],
        MailEvent.WEBSITE_CONTACT: [mail_contact_business],
        MailEvent.WEBSITE_BULK: [mail_bulk],
    }

    @classmethod
    def get_events(cls, event_id: MailEvent | str) -> list[Callable]:
        events = cls.events.get(event_id, [])
        if not events:
            log.error(f"Event {event_id} not found")
        return events

    @classmethod
    def trigger_events(
        cls,
        s: Session,
        event_id: MailEvent | str,
        _email: Email | None = None,
        **kwargs,
    ) -> bool:
        # Remember error state
        all_results = True

        for event in cls.get_events(event_id):
            status_id = EmailStatusId.QUEUED

            # Send immediately if not using worker
            if _email or not config.EMAIL_WORKER:
                try:
                    result = event(s, **kwargs)
                except Exception:
                    result = False
                    all_results = False
                    log.error(
                        f"Error sending {config.EMAIL_METHOD} email", exc_info=True
                    )
                if result:
                    status_id = EmailStatusId.SENT
                else:
                    status_id = EmailStatusId.FAILED

            # Save email in database
            if _email is None:
                _email = Email(
                    event_id=event_id,
                    data=kwargs,
                    user_id=current_user.id if current_user else None,
                    status_id=status_id,
                )
                s.add(_email)
            else:
                _email.updated_at = datetime.utcnow()
                _email.status_id = status_id
                s.flush()

        return all_results


mail = Mail()
