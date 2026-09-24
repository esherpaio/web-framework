from datetime import datetime, timezone
from typing import Callable

from sqlalchemy.orm import Session

from web.auth import current_user
from web.database.model import Email, EmailStatusId, EmailType
from web.logger import log
from web.setup import config
from web.utils import Singleton

from .classification import classify_email
from .enum import MailEvent


class Mail(metaclass=Singleton):
    events: dict[MailEvent | str, list[Callable]] = {}

    @classmethod
    def get_events(cls, event_id: MailEvent | str) -> list[Callable]:
        events = cls.events.get(event_id, [])
        if not events:
            log.error(f"Mail event {event_id} not found")
        return events

    @classmethod
    def trigger_events(
        cls,
        s: Session,
        event_id: MailEvent | str,
        user_id: int | None = None,
        _email: Email | None = None,
        scheduled_at: datetime | None = None,
        **kwargs,
    ) -> bool:
        if _email is not None and not isinstance(_email, Email):
            raise TypeError("Expected an Email instance")
        if _email is not None and _email.status_id == EmailStatusId.SKIPPED:
            return True

        events = cls.get_events(event_id)
        if not events:
            if _email is not None:
                _email.status_id = EmailStatusId.SKIPPED
                s.flush()
            return False

        send_now = _email is not None or not config.WORKER_ENABLED
        if _email is None:
            type_, digest = classify_email(s, event_id, kwargs)
            if user_id is None and current_user:
                user_id = current_user.id
            _email = Email(
                event_id=event_id,
                data=kwargs,
                user_id=user_id,
                scheduled_at=scheduled_at,
                type=type_,
                content_hash=digest,
                status_id=EmailStatusId.QUEUED,
            )
            s.add(_email)

        success = True
        if _email.type != EmailType.OK:
            _email.status_id = EmailStatusId.SKIPPED
        elif send_now:
            for event in events:
                try:
                    mail_success = event(s, **kwargs)
                except Exception:
                    mail_success = False
                if not mail_success:
                    success = False
            _email.updated_at = datetime.now(timezone.utc)
            _email.status_id = EmailStatusId.SENT if success else EmailStatusId.FAILED
        s.flush()

        message = f"Email {_email.id} for event {event_id} {_email.status_id}"
        if success:
            log.info(message)
        else:
            log.warning(message)
        return success


mail = Mail()
