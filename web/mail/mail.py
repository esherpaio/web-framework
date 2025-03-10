from datetime import datetime, timezone
from typing import Callable

from sqlalchemy.orm import Session

from web.auth import current_user
from web.config import config
from web.database.model import Email, EmailStatusId
from web.logger import log
from web.utils import Singleton

from .enum import MailEvent


class Mail(metaclass=Singleton):
    events: dict[MailEvent | str, list[Callable]] = {}

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
        all_result = True

        for event in cls.get_events(event_id):
            status_id = EmailStatusId.QUEUED

            # Send immediately if not using worker
            if _email or not config.WORKER_ENABLED:
                try:
                    result = event(s, **kwargs)
                except Exception:
                    result = False
                    all_result = False
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
                _email.updated_at = datetime.now(timezone.utc)
                _email.status_id = status_id
                s.flush()

        return all_result


mail = Mail()
