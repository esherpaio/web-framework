from datetime import datetime, timedelta, timezone

from sqlalchemy import null, or_

from web.database import conn
from web.database.model import Email, EmailStatusId
from web.logger import log

from .mail import mail


def send_emails(max_weeks: int = 4) -> None:
    while True:
        with conn.begin() as s:
            email = (
                s.query(Email)
                .filter(
                    Email.created_at
                    > datetime.now(timezone.utc) - timedelta(weeks=max_weeks),
                    or_(
                        Email.updated_at == null(),
                        Email.updated_at
                        < datetime.now(timezone.utc) - timedelta(days=1),
                    ),
                    Email.status_id.in_([EmailStatusId.QUEUED, EmailStatusId.FAILED]),
                )
                .order_by(Email.id.asc())
                .with_for_update(skip_locked=True)
                .first()
            )
            if not email:
                break
            log.info(
                f"Triggering email event {email.event_id} for user {email.user_id}"
            )
            mail.trigger_events(s, email.event_id, _email=email, **email.data)


if __name__ == "__main__":
    send_emails()
